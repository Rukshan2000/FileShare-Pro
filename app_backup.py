#!/usr/bin/env python3
import hashlib
import json
import os
import threading
import time
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_file
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max file size
app.config["ALLOWED_EXTENSIONS"] = {
    "txt",
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "zip",
    "doc",
    "docx",
    "xls",
    "xlsx",
}

socketio = SocketIO(app, cors_allowed_origins="*")

# Create uploads directory
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# File metadata storage
files_metadata = {}
METADATA_FILE = "files_metadata.json"

# Chat messages storage
chat_messages = []
MAX_CHAT_MESSAGES = 100  # Keep only last 100 messages


def load_metadata():
    global files_metadata
    try:
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, "r") as f:
                files_metadata = json.load(f)
    except:
        files_metadata = {}


def save_metadata():
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(files_metadata, f, indent=2)
    except:
        pass


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def get_file_size_mb(size_bytes):
    return round(size_bytes / (1024 * 1024), 2)


def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/files")
def files_page():
    return render_template("files.html")


@app.route("/chat")
def chat_page():
    return render_template("chat.html")


@app.route("/api/files")
def get_files():
    files_list = []
    for filename, metadata in files_metadata.items():
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(file_path):
            files_list.append(
                {
                    "name": filename,
                    "size": get_file_size_mb(metadata["size"]),
                    "upload_date": metadata["upload_date"],
                    "downloads": metadata.get("downloads", 0),
                    "md5": metadata.get("md5", ""),
                }
            )

    return jsonify(sorted(files_list, key=lambda x: x["upload_date"], reverse=True))


@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file selected"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        # Check if file already exists
        if os.path.exists(file_path):
            return jsonify({"error": "File already exists"}), 400

        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Calculate MD5
        file_md5 = calculate_md5(file_path)

        # Store metadata
        files_metadata[filename] = {
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "downloads": 0,
            "md5": file_md5,
        }
        save_metadata()

        # Notify all clients
        socketio.emit(
            "file_uploaded",
            {
                "filename": filename,
                "size": get_file_size_mb(file_size),
                "upload_date": files_metadata[filename]["upload_date"],
            },
        )

        return jsonify(
            {
                "message": "File uploaded successfully",
                "filename": filename,
                "size": get_file_size_mb(file_size),
                "md5": file_md5,
            }
        )

    return jsonify({"error": "File type not allowed"}), 400


@app.route("/api/download/<filename>")
def download_file(filename):
    if filename not in files_metadata:
        return jsonify({"error": "File not found"}), 404

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Update download count
    files_metadata[filename]["downloads"] += 1
    save_metadata()

    # Notify download
    socketio.emit(
        "file_downloaded",
        {"filename": filename, "downloads": files_metadata[filename]["downloads"]},
    )

    return send_file(file_path, as_attachment=True)


@app.route("/api/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    if filename not in files_metadata:
        return jsonify({"error": "File not found"}), 404

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        del files_metadata[filename]
        save_metadata()

        socketio.emit("file_deleted", {"filename": filename})
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "File not found"}), 404


@app.route("/api/stats")
def get_stats():
    total_files = len(files_metadata)
    total_size = sum(meta["size"] for meta in files_metadata.values())
    total_downloads = sum(meta.get("downloads", 0) for meta in files_metadata.values())

    return jsonify(
        {
            "total_files": total_files,
            "total_size_mb": get_file_size_mb(total_size),
            "total_downloads": total_downloads,
        }
    )


@socketio.on("connect")
def handle_connect():
    emit("connected", {"message": "Connected to file sharing server"})
    # Send recent chat messages to newly connected user
    emit("chat_history", {"messages": chat_messages[-20:]})  # Send last 20 messages


@socketio.on("chat_message")
def handle_chat_message(data):
    username = data.get("username", "Anonymous")
    message = data.get("message", "").strip()

    if message:
        chat_data = {
            "username": username,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "id": len(chat_messages) + 1,
        }

        chat_messages.append(chat_data)

        # Keep only last MAX_CHAT_MESSAGES messages
        if len(chat_messages) > MAX_CHAT_MESSAGES:
            chat_messages.pop(0)

        # Broadcast message to all connected clients
        emit("new_message", chat_data, broadcast=True)


@socketio.on("user_typing")
def handle_typing(data):
    username = data.get("username", "Anonymous")
    emit("user_typing", {"username": username}, broadcast=True, include_self=False)


@socketio.on("user_stop_typing")
def handle_stop_typing(data):
    username = data.get("username", "Anonymous")
    emit("user_stop_typing", {"username": username}, broadcast=True, include_self=False)


def cleanup_old_files():
    """Background task to clean up files older than 7 days"""
    while True:
        time.sleep(3600)  # Run every hour
        current_time = time.time()
        for filename, metadata in list(files_metadata.items()):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            upload_time = datetime.fromisoformat(metadata["upload_date"]).timestamp()

            if current_time - upload_time > 7 * 24 * 3600:  # 7 days
                if os.path.exists(file_path):
                    os.remove(file_path)
                del files_metadata[filename]

        save_metadata()


if __name__ == "__main__":
    load_metadata()

    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
    cleanup_thread.start()

    print("🚀 Professional File Sharing Server Starting...")
    print("📁 Upload folder:", app.config["UPLOAD_FOLDER"])
    print("🌐 Server running at: http://localhost:8000")
    print(
        "💡 Features: Real-time updates, File validation, MD5 checksums, Auto-cleanup, Group Chat"
    )

    socketio.run(app, host="0.0.0.0", port=8000, debug=True)

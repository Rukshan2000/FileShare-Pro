#!/usr/bin/env python3
import hashlib
import json
import mimetypes
import os
import secrets
import threading
import time
import uuid
from datetime import datetime, timedelta

from flask import (
    Flask,
    Response,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_socketio import SocketIO, emit
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(32)  # Generate a secure secret key
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

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Create uploads directory
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# File metadata storage
files_metadata = {}
METADATA_FILE = "files_metadata.json"

# Shareable links storage
share_links = {}
SHARE_LINKS_FILE = "share_links.json"

# API keys for programmatic access
api_keys = {}
API_KEYS_FILE = "api_keys.json"

# User authentication storage
users = {}
USERS_FILE = "users.json"

# Chat messages storage
chat_messages = []
MAX_CHAT_MESSAGES = 100  # Keep only last 100 messages


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

    @staticmethod
    def get(username):
        if username in users:
            return User(username)
        return None


@login_manager.user_loader
def load_user(username):
    return User.get(username)


# Create thumbnails directory
THUMBNAILS_FOLDER = "thumbnails"
os.makedirs(THUMBNAILS_FOLDER, exist_ok=True)


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


def load_share_links():
    global share_links
    try:
        if os.path.exists(SHARE_LINKS_FILE):
            with open(SHARE_LINKS_FILE, "r") as f:
                share_links = json.load(f)
    except:
        share_links = {}


def save_share_links():
    try:
        with open(SHARE_LINKS_FILE, "w") as f:
            json.dump(share_links, f, indent=2)
    except:
        pass


def load_api_keys():
    global api_keys
    try:
        if os.path.exists(API_KEYS_FILE):
            with open(API_KEYS_FILE, "r") as f:
                api_keys = json.load(f)
    except:
        api_keys = {}


def save_api_keys():
    try:
        with open(API_KEYS_FILE, "w") as f:
            json.dump(api_keys, f, indent=2)
    except:
        pass


def load_users():
    global users
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        else:
            # Create default admin user if no users exist
            create_default_admin()
    except:
        users = {}
        create_default_admin()


def save_users():
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except:
        pass


def create_default_admin():
    """Create a default admin user with username: admin, password: admin"""
    global users
    if "admin" not in users:
        users["admin"] = {
            "username": "admin",
            "password_hash": generate_password_hash("admin"),
            "role": "admin",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
        }
        save_users()
        print("Default admin user created - Username: admin, Password: admin")
        print("Please change the default password after first login!")


def create_user(username, password, role="user"):
    """Create a new user"""
    if username in users:
        return False, "User already exists"

    users[username] = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "role": role,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
    }
    save_users()
    return True, "User created successfully"


def verify_user(username, password):
    """Verify user credentials"""
    if username not in users:
        return False

    user_data = users[username]
    if check_password_hash(user_data["password_hash"], password):
        # Update last login
        users[username]["last_login"] = datetime.now().isoformat()
        save_users()
        return True
    return False


def verify_api_key(api_key):
    """Verify API key for programmatic access"""
    return api_key in api_keys and api_keys[api_key].get("active", True)


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


def create_folder_path(folder_path):
    """Create nested folder structure in uploads directory"""
    if not folder_path:
        return app.config["UPLOAD_FOLDER"]

    # Sanitize folder path
    folder_parts = [secure_filename(part) for part in folder_path.split("/") if part]
    full_path = os.path.join(app.config["UPLOAD_FOLDER"], *folder_parts)

    # Create directory if it doesn't exist
    os.makedirs(full_path, exist_ok=True)
    return full_path


def generate_share_link(filename, folder_path=""):
    """Generate a shareable link for a file"""
    share_token = secrets.token_urlsafe(32)
    expiry_date = datetime.now() + timedelta(days=7)  # Links expire after 7 days

    share_links[share_token] = {
        "filename": filename,
        "folder_path": folder_path,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiry_date.isoformat(),
        "download_count": 0,
        "max_downloads": None,  # No limit by default
    }
    save_share_links()
    return share_token


def create_thumbnail(file_path, filename):
    """Create thumbnail for image files"""
    try:
        # Check if file is an image
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            return None

        # Create thumbnail
        with Image.open(file_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # Create thumbnail
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Save thumbnail
            thumb_filename = f"thumb_{filename}.jpg"
            thumb_path = os.path.join(THUMBNAILS_FOLDER, thumb_filename)
            img.save(thumb_path, "JPEG", quality=85)
            return thumb_filename
    except Exception as e:
        print(f"Error creating thumbnail for {filename}: {str(e)}")
        return None


def is_image_file(filename):
    """Check if file is an image"""
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
    return os.path.splitext(filename.lower())[1] in image_extensions


# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html")

        if verify_user(username, password):
            user = User(username)
            login_user(user, remember=remember)
            flash(f"Welcome back, {username}!", "success")

            # Redirect to next page or home
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f"Goodbye, {username}!", "info")
    return redirect(url_for("login"))


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([current_password, new_password, confirm_password]):
            flash("All fields are required.", "error")
            return render_template("change_password.html")

        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return render_template("change_password.html")

        if len(new_password) < 4:
            flash("Password must be at least 4 characters long.", "error")
            return render_template("change_password.html")

        if not verify_user(current_user.username, current_password):
            flash("Current password is incorrect.", "error")
            return render_template("change_password.html")

        # Update password
        users[current_user.username]["password_hash"] = generate_password_hash(
            new_password
        )
        save_users()

        flash("Password changed successfully!", "success")
        return redirect(url_for("index"))

    return render_template("change_password.html")


# Protected application routes
@app.route("/")
@login_required
def index():
    return render_template("index.html", current_user=current_user)


@app.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html", current_user=current_user)


@app.route("/files")
@login_required
def files_page():
    return render_template("files.html", current_user=current_user)


@app.route("/chat")
@login_required
def chat_page():
    return render_template("chat.html", current_user=current_user)


@app.route("/api/files")
@login_required
def get_files():
    files_list = []

    # Get folder structure
    def scan_directory(current_path, relative_path=""):
        items = []
        try:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                relative_item_path = (
                    os.path.join(relative_path, item).replace("\\", "/")
                    if relative_path
                    else item
                )

                if os.path.isdir(item_path):
                    # It's a folder
                    items.append(
                        {
                            "name": item,
                            "type": "folder",
                            "path": relative_item_path,
                            "children": scan_directory(item_path, relative_item_path),
                        }
                    )
                else:
                    # It's a file
                    file_key = relative_item_path.replace("\\", "/")
                    if file_key in files_metadata:
                        metadata = files_metadata[file_key]

                        # Find share token for this file
                        share_token = None
                        folder_path = metadata.get("folder_path", "")
                        for token, link_data in share_links.items():
                            if (
                                link_data["filename"] == item
                                and link_data["folder_path"] == folder_path
                            ):
                                share_token = token
                                break

                        # Generate share token if none exists
                        if not share_token:
                            share_token = generate_share_link(item, folder_path)

                        file_info = {
                            "name": item,
                            "type": "file",
                            "path": relative_item_path,
                            "size": get_file_size_mb(metadata["size"]),
                            "upload_date": metadata["upload_date"],
                            "downloads": metadata.get("downloads", 0),
                            "md5": metadata.get("md5", ""),
                            "folder_path": relative_path,
                            "mime_type": mimetypes.guess_type(item)[0]
                            or "application/octet-stream",
                            "share_token": share_token,
                        }

                        # Add URLs if share token exists
                        if share_token:
                            file_info["urls"] = {
                                "direct": f"/file/{share_token}",
                                "preview": f"/preview/{share_token}",
                                "download": f"/share/{share_token}",
                            }

                            # Add thumbnail URL for images
                            if is_image_file(item):
                                thumb_filename = f"thumb_{item}.jpg"
                                thumb_path = os.path.join(
                                    THUMBNAILS_FOLDER, thumb_filename
                                )
                                if os.path.exists(thumb_path):
                                    file_info["urls"][
                                        "thumbnail"
                                    ] = f"/thumbnail/{thumb_filename}"

                        items.append(file_info)
        except PermissionError:
            pass
        return items

    return jsonify(scan_directory(app.config["UPLOAD_FOLDER"]))


@app.route("/api/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file selected"}), 400

    file = request.files["file"]
    folder_path = request.form.get("folder_path", "").strip()

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Create folder path
        upload_folder = create_folder_path(folder_path)
        file_path = os.path.join(upload_folder, filename)

        # Create unique filename if file exists
        counter = 1
        original_filename = filename
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            file_path = os.path.join(upload_folder, filename)
            counter += 1

        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Calculate MD5
        file_md5 = calculate_md5(file_path)

        # Store metadata with folder path
        file_key = (
            os.path.join(folder_path, filename).replace("\\", "/")
            if folder_path
            else filename
        )
        files_metadata[file_key] = {
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "downloads": 0,
            "md5": file_md5,
            "folder_path": folder_path,
            "original_name": original_filename,
        }
        save_metadata()

        # Generate shareable link
        share_token = generate_share_link(filename, folder_path)

        # Create thumbnail if it's an image
        thumbnail = None
        if is_image_file(filename):
            thumbnail = create_thumbnail(file_path, filename)

        # Notify all clients
        socketio.emit(
            "file_uploaded",
            {
                "filename": filename,
                "folder_path": folder_path,
                "size": get_file_size_mb(file_size),
                "upload_date": files_metadata[file_key]["upload_date"],
                "share_link": f"/share/{share_token}",
                "preview_url": f"/preview/{share_token}"
                if is_image_file(filename)
                else None,
                "thumbnail_url": f"/thumbnail/{thumbnail}" if thumbnail else None,
            },
        )

        return jsonify(
            {
                "message": "File uploaded successfully",
                "filename": filename,
                "folder_path": folder_path,
                "size": get_file_size_mb(file_size),
                "md5": file_md5,
                "share_link": f"/share/{share_token}",
                "preview_url": f"/preview/{share_token}"
                if is_image_file(filename)
                else None,
                "thumbnail_url": f"/thumbnail/{thumbnail}" if thumbnail else None,
                "direct_url": f"/file/{share_token}",
            }
        )

    return jsonify({"error": "File type not allowed"}), 400


@app.route("/api/download/<path:filepath>")
def download_file(filepath):
    file_key = filepath.replace("\\", "/")
    if file_key not in files_metadata:
        return jsonify({"error": "File not found"}), 404

    metadata = files_metadata[file_key]
    folder_path = metadata.get("folder_path", "")
    filename = os.path.basename(filepath)

    if folder_path:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_path, filename)
    else:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Update download count
    files_metadata[file_key]["downloads"] += 1
    save_metadata()

    # Notify download
    socketio.emit(
        "file_downloaded",
        {
            "filename": filename,
            "folder_path": folder_path,
            "downloads": files_metadata[file_key]["downloads"],
        },
    )

    return send_file(file_path, as_attachment=True, download_name=filename)


@app.route("/share/<share_token>")
def share_download(share_token):
    if share_token not in share_links:
        return jsonify({"error": "Invalid or expired share link"}), 404

    link_data = share_links[share_token]

    # Check if link has expired
    if datetime.now() > datetime.fromisoformat(link_data["expires_at"]):
        del share_links[share_token]
        save_share_links()
        return jsonify({"error": "Share link has expired"}), 410

    # Check download limit
    if (
        link_data.get("max_downloads")
        and link_data["download_count"] >= link_data["max_downloads"]
    ):
        return jsonify({"error": "Download limit reached"}), 410

    filename = link_data["filename"]
    folder_path = link_data["folder_path"]

    if folder_path:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_path, filename)
        file_key = os.path.join(folder_path, filename).replace("\\", "/")
    else:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file_key = filename

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    # Update download counts
    share_links[share_token]["download_count"] += 1
    if file_key in files_metadata:
        files_metadata[file_key]["downloads"] += 1
        save_metadata()

    save_share_links()

    return send_file(file_path, as_attachment=True, download_name=filename)


@app.route("/api/generate-share-link/<path:filepath>", methods=["POST"])
def generate_file_share_link(filepath):
    file_key = filepath.replace("\\", "/")
    if file_key not in files_metadata:
        return jsonify({"error": "File not found"}), 404

    metadata = files_metadata[file_key]
    folder_path = metadata.get("folder_path", "")
    filename = os.path.basename(filepath)

    # Get optional parameters
    data = request.get_json() or {}
    max_downloads = data.get("max_downloads")
    expires_in_days = data.get("expires_in_days", 7)

    share_token = secrets.token_urlsafe(32)
    expiry_date = datetime.now() + timedelta(days=expires_in_days)

    share_links[share_token] = {
        "filename": filename,
        "folder_path": folder_path,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiry_date.isoformat(),
        "download_count": 0,
        "max_downloads": max_downloads,
    }
    save_share_links()

    return jsonify(
        {
            "share_link": f"/share/{share_token}",
            "expires_at": expiry_date.isoformat(),
            "max_downloads": max_downloads,
        }
    )


@app.route("/api/create-folder", methods=["POST"])
def create_folder():
    data = request.get_json()
    folder_path = data.get("folder_path", "").strip()

    if not folder_path:
        return jsonify({"error": "Folder path is required"}), 400

    try:
        full_path = create_folder_path(folder_path)
        return jsonify(
            {
                "message": "Folder created successfully",
                "folder_path": folder_path,
                "full_path": full_path,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Failed to create folder: {str(e)}"}), 400


# S3/Minio-like API endpoints
@app.route("/file/<share_token>")
def serve_file_direct(share_token):
    """Direct file access - like S3 object URL"""
    if share_token not in share_links:
        abort(404)

    link_data = share_links[share_token]

    # Check if link has expired
    if datetime.now() > datetime.fromisoformat(link_data["expires_at"]):
        del share_links[share_token]
        save_share_links()
        abort(410)

    filename = link_data["filename"]
    folder_path = link_data["folder_path"]

    if folder_path:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_path, filename)
    else:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        abort(404)

    # Get MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    return send_file(file_path, mimetype=mime_type)


@app.route("/preview/<share_token>")
def serve_file_preview(share_token):
    """Preview file in browser - like S3 preview URL"""
    if share_token not in share_links:
        abort(404)

    link_data = share_links[share_token]

    # Check if link has expired
    if datetime.now() > datetime.fromisoformat(link_data["expires_at"]):
        del share_links[share_token]
        save_share_links()
        abort(410)

    filename = link_data["filename"]
    folder_path = link_data["folder_path"]

    if folder_path:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_path, filename)
    else:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        abort(404)

    # Get MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Force inline display for preview
    return send_file(file_path, mimetype=mime_type, as_attachment=False)


@app.route("/thumbnail/<thumbnail_filename>")
def serve_thumbnail(thumbnail_filename):
    """Serve thumbnail images"""
    thumb_path = os.path.join(THUMBNAILS_FOLDER, thumbnail_filename)
    if not os.path.exists(thumb_path):
        abort(404)

    return send_file(thumb_path, mimetype="image/jpeg")


# API endpoints for programmatic access (Laravel compatible)
@app.route("/api/v1/upload", methods=["POST"])
def api_upload_file():
    """API endpoint for programmatic file uploads"""
    # Check API key
    api_key = request.headers.get("X-API-Key") or request.form.get("api_key")
    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Invalid or missing API key"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    folder_path = request.form.get("folder_path", "").strip()
    generate_preview = request.form.get("generate_preview", "true").lower() == "true"

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Create folder path
        upload_folder = create_folder_path(folder_path)
        file_path = os.path.join(upload_folder, filename)

        # Create unique filename if file exists
        counter = 1
        original_filename = filename
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            file_path = os.path.join(upload_folder, filename)
            counter += 1

        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Calculate MD5
        file_md5 = calculate_md5(file_path)

        # Store metadata with folder path
        file_key = (
            os.path.join(folder_path, filename).replace("\\", "/")
            if folder_path
            else filename
        )
        files_metadata[file_key] = {
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "downloads": 0,
            "md5": file_md5,
            "folder_path": folder_path,
            "original_name": original_filename,
            "api_upload": True,
            "api_key": api_key,
        }
        save_metadata()

        # Generate shareable link
        share_token = generate_share_link(filename, folder_path)

        # Create thumbnail if it's an image and preview is requested
        thumbnail = None
        if generate_preview and is_image_file(filename):
            thumbnail = create_thumbnail(file_path, filename)

        # Prepare response
        response_data = {
            "success": True,
            "message": "File uploaded successfully",
            "data": {
                "filename": filename,
                "original_name": original_filename,
                "folder_path": folder_path,
                "size_mb": get_file_size_mb(file_size),
                "size_bytes": file_size,
                "md5": file_md5,
                "upload_date": files_metadata[file_key]["upload_date"],
                "urls": {
                    "download": f"/share/{share_token}",
                    "direct": f"/file/{share_token}",
                    "preview": f"/preview/{share_token}"
                    if is_image_file(filename)
                    else None,
                    "thumbnail": f"/thumbnail/{thumbnail}" if thumbnail else None,
                },
                "share_token": share_token,
                "mime_type": mimetypes.guess_type(filename)[0],
            },
        }

        # Notify via socket if requested
        if request.form.get("notify", "false").lower() == "true":
            socketio.emit(
                "file_uploaded",
                {
                    "filename": filename,
                    "folder_path": folder_path,
                    "size": get_file_size_mb(file_size),
                    "upload_date": files_metadata[file_key]["upload_date"],
                    "api_upload": True,
                },
            )

        return jsonify(response_data)

    return jsonify({"error": "File type not allowed"}), 400


@app.route("/api/v1/upload/base64", methods=["POST"])
def api_upload_base64():
    """Upload file from base64 data - useful for Laravel"""
    # Check API key
    api_key = request.headers.get("X-API-Key")
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    if not api_key:
        api_key = data.get("api_key")

    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Invalid or missing API key"}), 401

    if "file_data" not in data or "filename" not in data:
        return jsonify({"error": "file_data and filename are required"}), 400

    try:
        import base64

        file_data = base64.b64decode(data["file_data"])
        filename = secure_filename(data["filename"])
        folder_path = data.get("folder_path", "").strip()

        if not allowed_file(filename):
            return jsonify({"error": "File type not allowed"}), 400

        # Create folder path
        upload_folder = create_folder_path(folder_path)
        file_path = os.path.join(upload_folder, filename)

        # Create unique filename if file exists
        counter = 1
        original_filename = filename
        while os.path.exists(file_path):
            name, ext = os.path.splitext(original_filename)
            filename = f"{name}_{counter}{ext}"
            file_path = os.path.join(upload_folder, filename)
            counter += 1

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_data)

        file_size = os.path.getsize(file_path)
        file_md5 = calculate_md5(file_path)

        # Store metadata
        file_key = (
            os.path.join(folder_path, filename).replace("\\", "/")
            if folder_path
            else filename
        )
        files_metadata[file_key] = {
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "downloads": 0,
            "md5": file_md5,
            "folder_path": folder_path,
            "original_name": original_filename,
            "api_upload": True,
            "api_key": api_key,
        }
        save_metadata()

        # Generate shareable link
        share_token = generate_share_link(filename, folder_path)

        # Create thumbnail if it's an image
        thumbnail = None
        if is_image_file(filename):
            thumbnail = create_thumbnail(file_path, filename)

        return jsonify(
            {
                "success": True,
                "message": "File uploaded successfully",
                "data": {
                    "filename": filename,
                    "original_name": original_filename,
                    "folder_path": folder_path,
                    "size_mb": get_file_size_mb(file_size),
                    "size_bytes": file_size,
                    "md5": file_md5,
                    "upload_date": files_metadata[file_key]["upload_date"],
                    "urls": {
                        "download": f"/share/{share_token}",
                        "direct": f"/file/{share_token}",
                        "preview": f"/preview/{share_token}"
                        if is_image_file(filename)
                        else None,
                        "thumbnail": f"/thumbnail/{thumbnail}" if thumbnail else None,
                    },
                    "share_token": share_token,
                    "mime_type": mimetypes.guess_type(filename)[0],
                },
            }
        )

    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route("/api/v1/generate-key", methods=["POST"])
def generate_api_key():
    """Generate a new API key"""
    admin_key = request.headers.get("X-Admin-Key")
    if admin_key != "your-admin-secret-key":  # Change this to a secure admin key
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    key_name = data.get("name", f"API Key {len(api_keys) + 1}")

    new_api_key = secrets.token_urlsafe(32)
    api_keys[new_api_key] = {
        "name": key_name,
        "created_at": datetime.now().isoformat(),
        "active": True,
        "usage_count": 0,
    }
    save_api_keys()

    return jsonify(
        {
            "success": True,
            "api_key": new_api_key,
            "name": key_name,
            "created_at": api_keys[new_api_key]["created_at"],
        }
    )


@app.route("/api/v1/files", methods=["GET"])
def api_get_files():
    """API endpoint to get file list"""
    api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
    if not api_key or not verify_api_key(api_key):
        return jsonify({"error": "Invalid or missing API key"}), 401

    folder_path = request.args.get("folder_path", "").strip()

    files_list = []
    for file_key, metadata in files_metadata.items():
        if folder_path and not file_key.startswith(folder_path):
            continue

        filename = os.path.basename(file_key)
        file_folder = metadata.get("folder_path", "")

        if folder_path:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_folder, filename)
        else:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        if os.path.exists(file_path):
            # Find share token for this file
            share_token = None
            for token, link_data in share_links.items():
                if (
                    link_data["filename"] == filename
                    and link_data["folder_path"] == file_folder
                ):
                    share_token = token
                    break

            file_info = {
                "filename": filename,
                "original_name": metadata.get("original_name", filename),
                "folder_path": file_folder,
                "size_mb": get_file_size_mb(metadata["size"]),
                "size_bytes": metadata["size"],
                "upload_date": metadata["upload_date"],
                "downloads": metadata.get("downloads", 0),
                "md5": metadata.get("md5", ""),
                "mime_type": mimetypes.guess_type(filename)[0],
            }

            if share_token:
                file_info["urls"] = {
                    "download": f"/share/{share_token}",
                    "direct": f"/file/{share_token}",
                    "preview": f"/preview/{share_token}"
                    if is_image_file(filename)
                    else None,
                }

            files_list.append(file_info)

    return jsonify(
        {
            "success": True,
            "files": sorted(files_list, key=lambda x: x["upload_date"], reverse=True),
            "total_files": len(files_list),
        }
    )


@app.route("/api/delete/<path:filepath>", methods=["DELETE"])
def delete_file(filepath):
    file_key = filepath.replace("\\", "/")
    if file_key not in files_metadata:
        return jsonify({"error": "File not found"}), 404

    metadata = files_metadata[file_key]
    folder_path = metadata.get("folder_path", "")
    filename = os.path.basename(filepath)

    if folder_path:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_path, filename)
    else:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        del files_metadata[file_key]
        save_metadata()

        # Remove associated share links
        to_remove = []
        for token, link_data in share_links.items():
            if (
                link_data["filename"] == filename
                and link_data["folder_path"] == folder_path
            ):
                to_remove.append(token)

        for token in to_remove:
            del share_links[token]
        save_share_links()

        socketio.emit(
            "file_deleted", {"filename": filename, "folder_path": folder_path}
        )
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "File not found"}), 404


@app.route("/api/stats")
@login_required
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


@app.route("/api/create-folder", methods=["POST"])
def create_folder_api():
    data = request.get_json()
    folder_path = data.get("folder_path", "").strip()

    if not folder_path:
        return jsonify({"error": "Folder path is required"}), 400

    # Validate folder path
    if ".." in folder_path or folder_path.startswith("/"):
        return jsonify({"error": "Invalid folder path"}), 400

    try:
        # Create the folder path
        full_folder_path = create_folder_path(folder_path)

        return jsonify(
            {
                "message": f'Folder "{folder_path}" created successfully',
                "folder_path": folder_path,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat/upload", methods=["POST"])
def upload_chat_file():
    if "file" not in request.files:
        return jsonify({"error": "No file selected"}), 400

    username = request.form.get("username", "Anonymous")
    folder_path = request.form.get("folder_path", "chat").strip()
    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        # Generate unique filename to avoid conflicts
        timestamp = int(time.time() * 1000)
        original_filename = secure_filename(file.filename)
        filename = f"chat_{timestamp}_{original_filename}"

        # Create folder path for chat uploads
        upload_folder = create_folder_path(folder_path)
        file_path = os.path.join(upload_folder, filename)

        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Calculate MD5
        file_md5 = calculate_md5(file_path)

        # Store metadata
        file_key = (
            os.path.join(folder_path, filename).replace("\\", "/")
            if folder_path
            else filename
        )
        files_metadata[file_key] = {
            "size": file_size,
            "upload_date": datetime.now().isoformat(),
            "downloads": 0,
            "md5": file_md5,
            "original_name": original_filename,
            "chat_upload": True,
            "uploaded_by": username,
            "folder_path": folder_path,
        }
        save_metadata()

        # Generate shareable link
        share_token = generate_share_link(filename, folder_path)

        # Determine file type for chat message
        file_extension = original_filename.rsplit(".", 1)[1].lower()
        is_image = file_extension in {"png", "jpg", "jpeg", "gif"}

        # Create chat message for the file
        chat_data = {
            "username": username,
            "message": f"shared a {'image' if is_image else 'file'}",
            "timestamp": datetime.now().isoformat(),
            "id": len(chat_messages) + 1,
            "type": "image" if is_image else "file",
            "file_data": {
                "filename": filename,
                "original_name": original_filename,
                "folder_path": folder_path,
                "size": get_file_size_mb(file_size),
                "md5": file_md5,
                "share_link": f"/share/{share_token}",
            },
        }

        chat_messages.append(chat_data)

        # Keep only last MAX_CHAT_MESSAGES messages
        if len(chat_messages) > MAX_CHAT_MESSAGES:
            chat_messages.pop(0)

        # Broadcast file message to all connected clients
        socketio.emit("new_message", chat_data)

        return jsonify(
            {
                "message": "File uploaded successfully",
                "filename": filename,
                "original_name": original_filename,
                "folder_path": folder_path,
                "size": get_file_size_mb(file_size),
                "type": "image" if is_image else "file",
                "share_link": f"/share/{share_token}",
            }
        )

    return jsonify({"error": "File type not allowed"}), 400


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
            "type": "text",  # Default to text message
        }

        chat_messages.append(chat_data)

        # Keep only last MAX_CHAT_MESSAGES messages
        if len(chat_messages) > MAX_CHAT_MESSAGES:
            chat_messages.pop(0)

        # Broadcast message to all connected clients
        emit("new_message", chat_data, broadcast=True)

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
    load_share_links()
    load_api_keys()
    load_users()  # Load user authentication data

    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
    cleanup_thread.start()

    print("🚀 Professional File Sharing Server Starting...")
    print("📁 Upload folder:", app.config["UPLOAD_FOLDER"])
    print("🖼️  Thumbnails folder:", THUMBNAILS_FOLDER)
    print("🌐 Server running at: http://localhost:8000")
    print("🔑 API endpoints available at: http://localhost:8000/api/v1/")
    print("👤 Default admin login - Username: admin, Password: admin")
    print(
        "💡 Features: Real-time updates, File validation, MD5 checksums, Auto-cleanup, Group Chat, Shareable Links, Custom Folders, S3-like URLs, API Access"
    )

    socketio.run(app, host="0.0.0.0", port=8000, debug=True)

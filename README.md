# FileShare Pro 🚀

A modern, professional file sharing web application built with Flask and Socket.IO. Features real-time updates, secure file handling, group chat functionality, and a beautiful responsive interface.

## ✨ Features

### 📁 File Management
- **Secure File Upload**: Support for multiple file types (images, documents, archives)
- **Real-time File Updates**: Instant notifications when files are uploaded/downloaded
- **File Validation**: MD5 checksum verification for file integrity
- **Download Tracking**: Monitor file download statistics
- **Auto Cleanup**: Automatic deletion of files older than 7 days
- **File Size Limit**: 100MB maximum file size for optimal performance

### 💬 Real-time Chat
- **Group Chat**: Real-time messaging with all connected users
- **File Sharing in Chat**: Upload and share images/files directly in chat
- **Typing Indicators**: See when other users are typing
- **Message History**: Persistent chat history (last 100 messages)
- **User-friendly Interface**: Clean, modern chat interface

### 🔒 Security Features
- **Secure Filename Handling**: Protection against malicious filenames
- **File Type Validation**: Only allowed file extensions can be uploaded
- **MD5 Checksums**: File integrity verification
- **CORS Protection**: Secure cross-origin resource sharing

### 📊 Analytics & Monitoring
- **Live Statistics**: Real-time file count, total size, and download metrics
- **File Metadata**: Detailed information about each uploaded file
- **Download Counters**: Track file popularity

## 🛠️ Tech Stack

- **Backend**: Flask (Python web framework)
- **Real-time Communication**: Socket.IO for WebSocket connections
- **Frontend**: Vanilla JavaScript with modern CSS
- **File Handling**: Werkzeug for secure file operations
- **Data Storage**: JSON-based metadata storage

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone/Download the project**
   ```bash
   cd file_sharing_app
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python3 app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:8000`
   - The application will be running on all network interfaces (0.0.0.0)

## 🎯 Usage

### File Upload
1. Navigate to the **Upload** page
2. Select files to upload (supports drag & drop)
3. Files are validated and stored securely
4. Real-time notifications inform all users of new uploads

### File Management
1. Visit the **Files** page to view all uploaded files
2. Download files directly or delete unwanted files
3. View file metadata including size, upload date, and download count

### Group Chat
1. Go to the **Chat** page
2. Enter your username and start chatting
3. Share files directly in chat by using the file upload feature
4. See real-time typing indicators and message history

## 📋 Supported File Types

- **Images**: PNG, JPG, JPEG, GIF
- **Documents**: PDF, TXT, DOC, DOCX, XLS, XLSX
- **Archives**: ZIP
- **Maximum file size**: 100MB per file

## 🔧 Configuration

The application can be customized by modifying the following settings in `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Max file size
app.config['ALLOWED_EXTENSIONS'] = {...}  # Allowed file extensions
MAX_CHAT_MESSAGES = 100  # Maximum chat history
```

## 📁 Project Structure

```
file_sharing_app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── files_metadata.json    # File metadata storage
├── static/
│   ├── style.css         # Application styles
│   └── script.js         # Frontend JavaScript
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── upload.html       # File upload page
│   ├── files.html        # File management page
│   └── chat.html         # Chat interface
└── uploads/              # Uploaded files directory
```

## 🌐 API Endpoints

### File Operations
- `GET /api/files` - Get list of all files
- `POST /api/upload` - Upload a new file
- `GET /api/download/<filename>` - Download a specific file
- `DELETE /api/delete/<filename>` - Delete a file
- `GET /api/stats` - Get server statistics

### Chat Operations
- `POST /api/chat/upload` - Upload file in chat
- WebSocket events for real-time chat functionality

## 🚀 Features in Detail

### Real-time Updates
The application uses Socket.IO to provide real-time updates:
- File upload notifications
- Download counters
- Chat messages
- Typing indicators
- User connection status

### Security Measures
- Secure filename sanitization using `secure_filename()`
- File type validation before upload
- MD5 checksum generation for integrity verification
- CORS protection for API endpoints
- File size limitations to prevent abuse

### Auto Cleanup
A background thread automatically removes files older than 7 days to manage disk space efficiently.

## 🎨 User Interface

The application features a modern, responsive design with:
- **Glass-morphism effects** for a modern look
- **Real-time statistics** on the homepage
- **Drag & drop file uploads** for better UX
- **Mobile-responsive design** for all devices
- **Professional color scheme** with gradient backgrounds

## 🔧 Development

To contribute to this project:

1. Follow the installation steps above
2. Make your changes
3. Test thoroughly on `http://localhost:8000`
4. Ensure all features work correctly

### Key Files to Modify
- `app.py` - Backend logic and API endpoints
- `templates/*.html` - Frontend pages and layouts
- `static/style.css` - Styling and visual design
- `static/script.js` - Frontend JavaScript functionality

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `app.py`: `socketio.run(app, host='0.0.0.0', port=8001)`

2. **Permission errors with uploads directory**
   - Ensure the `uploads` directory has proper write permissions

3. **File upload fails**
   - Check file size (must be under 100MB)
   - Verify file extension is in the allowed list

4. **Real-time features not working**
   - Ensure Socket.IO is properly connected (check browser console)
   - Verify no firewall blocking WebSocket connections

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using Flask, Socket.IO, and modern web technologies**

# FileShare Pro 🚀

A modern, professional file sharing web application built with Flask and Socket.IO. Features real-time updates, secure file handling, group chat functionality, **shareable links with multiple URL types**, **custom folder organization**, **S3/Minio-like media server capabilities**, **programmatic API access**, and a beautiful responsive interface.

## ✨ Features

### 📁 Advanced File Management
- **Custom Folder Structure**: Create and organize files in custom folder hierarchies
- **Secure File Upload**: Support for multiple file types (images, documents, archives)
- **Real-time File Updates**: Instant notifications when files are uploaded/downloaded
- **File Validation**: MD5 checksum verification for file integrity
- **Download Tracking**: Monitor file download statistics
- **Auto Cleanup**: Automatic deletion of files older than 7 days
- **File Size Limit**: 100MB maximum file size for optimal performance
- **Breadcrumb Navigation**: Easy navigation through folder structures with proper folder context
- **Increased Table Width**: Enhanced file browser with wider table layout for better viewing

### 🔗 Advanced Shareable Links System
- **4 Types of Share Links**: Generate different URL formats for various use cases:
  - **Preview Links**: View files directly in browser (images, PDFs, etc.)
  - **Direct Links**: S3/Minio-like direct file access URLs
  - **Download Links**: Force file download with attachment headers
  - **Thumbnail Links**: 300x300px JPEG thumbnails for images
- **Customizable Expiry**: Set link expiration (1-365 days)
- **Download Limits**: Optional maximum download count per link
- **Link Management**: Automatic cleanup of expired links
- **Secure Tokens**: 32-character secure tokens for link protection
- **4-Button Share Modal**: Separate buttons for each link type with color-coded interface
- **Copy to Clipboard**: Easy link sharing with one-click copy for each URL type
- **All URLs Display**: Modal showing all available URL types for any file

### 🌐 S3/Minio-like Media Server Features
- **Direct File Access**: CDN-like URLs for direct file serving
- **Preview Endpoints**: Browser-friendly file viewing
- **Thumbnail Generation**: Automatic thumbnail creation for images using Pillow
- **Multiple URL Formats**: Different endpoints for different access patterns
- **Token-based Security**: Secure access to all file endpoints

### 🔧 Programmatic API Access
- **RESTful API**: Full API access for integration with other applications
- **API Key Authentication**: Secure API access with generated keys
- **Laravel/PHP Integration**: Ready-to-use PHP code examples and SDK
- **Multiple Upload Formats**: Support for form-data and base64 uploads
- **Batch Operations**: Upload multiple files programmatically
- **Response Formats**: JSON responses with all URL types included

### 💬 Real-time Chat
- **Group Chat**: Real-time messaging with all connected users
- **File Sharing in Chat**: Upload and share images/files directly in chat with auto-generated share links
- **Typing Indicators**: See when other users are typing
- **Message History**: Persistent chat history (last 100 messages)
- **User-friendly Interface**: Clean, modern chat interface
- **Chat File Organization**: Chat uploads automatically organized in 'chat' folder

### 🔒 Security Features
- **Secure Filename Handling**: Protection against malicious filenames
- **File Type Validation**: Only allowed file extensions can be uploaded
- **MD5 Checksums**: File integrity verification
- **CORS Protection**: Secure cross-origin resource sharing
- **API Key Management**: Secure programmatic access control
- **Token Expiration**: Time-based security for all share links

### 📊 Analytics & Monitoring
- **Live Statistics**: Real-time file count, total size, and download metrics
- **File Metadata**: Detailed information about each uploaded file
- **Download Counters**: Track file popularity
- **API Usage Tracking**: Monitor programmatic API usage

## 🛠️ Tech Stack

- **Backend**: Flask (Python web framework) with advanced routing and API endpoints
- **Real-time Communication**: Socket.IO for WebSocket connections
- **Frontend**: Vanilla JavaScript with modern CSS and responsive design
- **File Handling**: Werkzeug for secure file operations
- **Image Processing**: Pillow for thumbnail generation and image manipulation
- **Data Storage**: JSON-based metadata storage with enhanced file tracking
- **API Security**: Token-based authentication for programmatic access

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

### File Upload & Organization
1. Navigate to the **Upload** page
2. **Optional**: Enter a custom folder path (e.g., "documents/2024", "projects/web-app")
3. Select files to upload (supports drag & drop)
4. Files are validated, stored securely, and organized in your specified folder structure
5. Each upload automatically generates a shareable link
6. Real-time notifications inform all users of new uploads

### File Management & Sharing
1. Visit the **Files** page to view all uploaded files and folders in a hierarchical structure
2. **Navigate folders** using the breadcrumb navigation or by clicking folder names
3. **Files display contextually** - only files within the current folder are shown
4. **Download files** directly or **generate custom share links with 4 different URL types**
5. **4 Share Link Types**:
   - **Preview Link**: View files directly in browser (images, PDFs, text files)
   - **Direct Link**: S3/Minio-like direct access URL for CDN usage
   - **Download Link**: Force file download with proper attachment headers
   - **Thumbnail Link**: 300x300px JPEG thumbnail for images (auto-generated)
6. **Share Link Options**:
   - Set expiration time (1-365 days)
   - Set maximum download limit (optional)
   - Copy any URL type to clipboard with one click
   - Open links directly in new tab for testing
7. View comprehensive file metadata including size, upload date, and download count
8. Delete unwanted files (automatically removes all associated share links)
9. **Enhanced UI**: Wider table layout with better organization and visual hierarchy

### Accessing Shared Files
1. **4 Different Access Methods**:
   - **Preview URLs**: `http://yourserver/preview/<token>` - View files in browser
   - **Direct URLs**: `http://yourserver/file/<token>` - Direct file access like S3/CDN
   - **Download URLs**: `http://yourserver/share/<token>` - Force download
   - **Thumbnail URLs**: `http://yourserver/thumbnail/<filename>?token=<token>` - Image thumbnails
2. **No Account Required**: All share links work without user registration
3. **Automatic Expiry**: Links expire based on the set timeframe
4. **Download Tracking**: All downloads through share links are tracked and counted
5. **Mobile Friendly**: All link types work perfectly on mobile devices

### Programmatic API Access
1. **Generate API Keys**: Use the admin interface to create API keys for your applications
2. **Multiple Integration Options**:
   - **Laravel/PHP**: Ready-to-use controller and service classes provided
   - **cURL**: Direct HTTP API calls
   - **Any Language**: RESTful JSON API works with any programming language
3. **Upload Methods**:
   - **Form Data**: Standard multipart/form-data uploads
   - **Base64**: Direct base64 string uploads for APIs
   - **Batch Upload**: Multiple files in single API call
4. **Response Format**: All API calls return complete URL sets for immediate use
5. **Integration Examples**: Complete code samples for Laravel, PHP, and cURL provided

### Group Chat & File Sharing
1. Go to the **Chat** page
2. Enter your username and start chatting
3. **Share files directly in chat** with built-in file upload (automatically creates share links)
4. Chat files are organized in the 'chat' folder automatically
5. See real-time typing indicators and message history

## 📋 Supported File Types

- **Images**: PNG, JPG, JPEG, GIF, WebP, BMP (auto-generates thumbnails)
- **Documents**: PDF, TXT, DOC, DOCX, XLS, XLSX (preview supported for some types)
- **Archives**: ZIP
- **Maximum file size**: 100MB per file
- **Thumbnail Generation**: Automatic for all image types with 300x300px JPEG output

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
├── app.py                 # Main Flask application with share links, S3-like URLs & API endpoints
├── requirements.txt       # Python dependencies (includes Pillow for thumbnails)
├── files_metadata.json    # File metadata storage (with folder paths & URL mappings)
├── share_links.json       # Shareable links storage (auto-generated with multiple URL types)
├── api_keys.json         # API key storage for programmatic access
├── API_DOCUMENTATION.md  # Complete API documentation with examples
├── static/
│   ├── style.css         # Application styles (enhanced with 4-button share modal & wider tables)
│   └── script.js         # Frontend JavaScript (folder navigation, share modals & URL management)
├── templates/
│   ├── base.html         # Base template with responsive design
│   ├── index.html        # Homepage with enhanced statistics
│   ├── upload.html       # File upload page (with folder input)
│   ├── files.html        # File management page (4-button share system & folder navigation)
│   └── chat.html         # Chat interface with integrated file sharing
├── examples/
│   └── laravel/          # Laravel integration examples
│       ├── FileShareController.php    # Complete Laravel controller
│       ├── FileShareService.php       # Service class for API integration
│       └── config/fileshare.php       # Configuration file
├── uploads/              # Uploaded files directory (supports nested folders)
│   ├── folder1/          # Example: custom folder structure
│   │   └── file1.txt
│   ├── documents/
│   │   └── 2024/
│   │       └── report.pdf
│   └── chat/             # Auto-created folder for chat uploads
│       └── shared_image.png
└── thumbnails/           # Auto-generated thumbnails directory
    └── filename_300x300.jpg
```

## 🌐 API Endpoints

### File Operations
- `GET /api/files` - Get hierarchical list of all files and folders
- `GET /api/files?folder=<path>` - Get files in specific folder
- `POST /api/upload` - Upload a new file (with optional folder_path parameter)
- `GET /api/download/<filepath>` - Download a specific file
- `DELETE /api/delete/<filepath>` - Delete a file
- `GET /api/stats` - Get server statistics
- `POST /api/create-folder` - Create a new folder structure

### Share Link Operations (Multiple URL Types)
- `POST /api/generate-share-link/<filepath>` - Generate all 4 types of shareable links
- `GET /share/<token>` - Download via shareable link (forces download)
- `GET /file/<token>` - Direct file access (S3/CDN-like URL)
- `GET /preview/<token>` - Preview file in browser
- `GET /thumbnail/<filename>?token=<token>` - Get 300x300px thumbnail (images only)

### Programmatic API (Requires API Key)
- `POST /api/v1/generate-key` - Generate new API key (admin only)
- `POST /api/v1/upload` - Upload file with form-data
- `POST /api/v1/upload-base64` - Upload file with base64 data
- `GET /api/v1/files` - List all files with complete URL sets
- `GET /api/v1/file/<filepath>` - Get file metadata with all URL types
- Headers required: `X-API-Key: your-api-key`

### Laravel/PHP Integration Endpoints
- All `/api/v1/*` endpoints are Laravel-compatible
- Returns complete URL sets in responses
- Includes thumbnail URLs for images
- Ready-to-use with provided Laravel service classes

### Chat Operations
- `POST /api/chat/upload` - Upload file in chat (with auto-folder organization)
- WebSocket events for real-time chat functionality

## 🚀 Features in Detail

### Real-time Updates
The application uses Socket.IO to provide real-time updates:
- File upload notifications with complete URL sets including all 4 link types
- Download counters and folder navigation updates
- Chat messages with integrated file sharing and auto-generated links
- Typing indicators and user presence
- User connection status and activity feeds

### Security Measures
- Secure filename sanitization using `secure_filename()`
- File type validation before upload with enhanced MIME type checking
- MD5 checksum generation for integrity verification
- **Secure share links** with time-based expiration and optional download limits
- **Token-based file access** using 32-character secure tokens for all URL types
- **API Key Authentication** for programmatic access with rate limiting
- CORS protection for API endpoints with configurable origins
- File size limitations to prevent abuse (100MB limit)
- **Thumbnail Security**: Secure thumbnail generation with token validation

### Auto Cleanup
A background thread automatically removes:
- Files older than 7 days to manage disk space efficiently
- Expired share links to maintain security (all URL types)
- Orphaned metadata entries and broken file references  
- Unused thumbnails from deleted images
- Expired API keys and inactive sessions

## 🎨 User Interface

The application features a modern, responsive design with:
- **Glass-morphism effects** for a modern look with enhanced visual depth
- **Hierarchical folder navigation** with breadcrumbs and proper context switching
- **Real-time statistics** on the homepage with enhanced metrics
- **Drag & drop file uploads** with folder path selection and progress tracking
- **4-Button Share Modal** with color-coded interface for different URL types
- **Enhanced File Browser** with wider table layout and better information density
- **Modal dialogs** for comprehensive file sharing and management
- **Individual URL Copy Buttons** in file table for quick access to any URL type
- **Mobile-responsive design** for all devices with touch-friendly interfaces
- **Professional color scheme** with gradient backgrounds and smooth transitions
- **Interactive file/folder browser** with context-aware navigation
- **Thumbnail Previews** integrated into file listings for better visual identification
- **Mobile-responsive design** for all devices
- **Professional color scheme** with gradient backgrounds
- **Interactive file/folder browser** with navigation

## 🔧 Development

### Laravel/PHP Integration

The application includes ready-to-use Laravel integration with complete examples:

#### Quick Setup for Laravel
```php
// Add to your .env file
FILESHARE_URL=http://localhost:8000
FILESHARE_API_KEY=your-generated-api-key

// Use the provided service class
$fileShare = new FileShareService();
$result = $fileShare->uploadFile($file, 'my-folder/subfolder');

// Get all URL types
echo $result['urls']['direct'];     // S3-like direct URL
echo $result['urls']['preview'];    // Browser preview URL  
echo $result['urls']['download'];   // Force download URL
echo $result['urls']['thumbnail'];  // Thumbnail URL (images only)
```

#### Complete Integration Files Provided
- `examples/laravel/FileShareController.php` - Full controller with all methods
- `examples/laravel/FileShareService.php` - Service class for API integration
- `examples/laravel/config/fileshare.php` - Configuration management

#### API Usage Examples
```bash
# Upload with cURL
curl -X POST http://localhost:8000/api/v1/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@image.jpg" \
  -F "folder_path=gallery/2024"

# Response includes all URL types
{
  "success": true,
  "urls": {
    "preview": "/preview/abc123token",
    "direct": "/file/abc123token", 
    "download": "/share/abc123token",
    "thumbnail": "/thumbnail/image.jpg?token=abc123token"
  }
}
```

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
   - Check folder path doesn't contain invalid characters

4. **Share links not working**
   - Ensure the link hasn't expired
   - Check if download limit has been reached
   - Verify the original file still exists
   - Try different URL types (preview, direct, download, thumbnail)

5. **API integration issues**
   - Verify API key is correctly generated and included in headers
   - Check API endpoint URLs match your server configuration
   - Ensure proper Content-Type headers for file uploads
   - Review API_DOCUMENTATION.md for complete examples

6. **Thumbnail generation fails**
   - Ensure Pillow is properly installed (`pip install Pillow==10.0.1`)
   - Check if uploaded file is a supported image format
   - Verify thumbnails directory has write permissions
   - Images must be valid format (corrupted images will fail)

7. **Folder navigation issues**
   - Check folder permissions in the uploads directory
   - Ensure folder names don't contain special characters
   - Verify folder structure matches the metadata in files_metadata.json
   - Try refreshing the file list to reload folder structure

6. **Real-time features not working**
   - Ensure Socket.IO is properly connected (check browser console)
   - Verify no firewall blocking WebSocket connections

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using Flask, Socket.IO, Pillow, and modern web technologies**

**✨ Latest Features:**
- **4 Share Link Types**: Preview, Direct, Download, and Thumbnail URLs
- **S3/Minio-like Media Server**: Direct file access with CDN-like URLs  
- **Programmatic API**: Full Laravel/PHP integration with examples
- **Enhanced Folder Navigation**: Context-aware file browsing
- **Auto Thumbnail Generation**: 300x300px thumbnails for all images
- **4-Button Share Modal**: Color-coded interface for different link types
- **Wider Table Layout**: Better file browser with enhanced information display

# FileShare Pro API Documentation 📡

This document provides comprehensive API documentation for programmatic access to FileShare Pro, including Laravel/PHP examples.

## 🔑 Authentication

All API endpoints require authentication via API key. Include your API key in one of the following ways:

### Method 1: Header Authentication (Recommended)
```bash
curl -H "X-API-Key: your-api-key-here" ...
```

### Method 2: Form/Query Parameter
```bash
curl -F "api_key=your-api-key-here" ...
```

## 🚀 Getting Started

### 1. Generate API Key

First, generate an API key using the admin endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/generate-key \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: your-admin-secret-key" \
  -d '{"name": "My Laravel App"}'
```

**Response:**
```json
{
  "success": true,
  "api_key": "abc123...",
  "name": "My Laravel App",
  "created_at": "2025-09-24T10:00:00"
}
```

## 📤 File Upload Endpoints

### 1. Upload File (Form Data)

**Endpoint:** `POST /api/v1/upload`

Upload files using multipart form data (similar to S3 POST uploads).

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@/path/to/image.jpg" \
  -F "folder_path=images/2024" \
  -F "generate_preview=true"
```

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "filename": "image.jpg",
    "original_name": "image.jpg",
    "folder_path": "images/2024",
    "size_mb": 2.5,
    "size_bytes": 2621440,
    "md5": "d41d8cd98f00b204e9800998ecf8427e",
    "upload_date": "2025-09-24T10:30:00.123456",
    "urls": {
      "download": "/share/abc123token",
      "direct": "/file/abc123token",
      "preview": "/preview/abc123token",
      "thumbnail": "/thumbnail/thumb_image.jpg.jpg"
    },
    "share_token": "abc123token",
    "mime_type": "image/jpeg"
  }
}
```

### 2. Upload Base64 File

**Endpoint:** `POST /api/v1/upload/base64`

Upload files as base64 encoded data (perfect for Laravel file uploads).

```bash
curl -X POST http://localhost:8000/api/v1/upload/base64 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "filename": "document.pdf",
    "file_data": "base64-encoded-file-content-here",
    "folder_path": "documents/2024"
  }'
```

## 📁 File Management Endpoints

### 3. Get File List

**Endpoint:** `GET /api/v1/files`

Get list of uploaded files with their URLs.

```bash
curl "http://localhost:8000/api/v1/files?folder_path=images" \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "filename": "image.jpg",
      "original_name": "image.jpg",
      "folder_path": "images/2024",
      "size_mb": 2.5,
      "size_bytes": 2621440,
      "upload_date": "2025-09-24T10:30:00.123456",
      "downloads": 5,
      "md5": "d41d8cd98f00b204e9800998ecf8427e",
      "mime_type": "image/jpeg",
      "urls": {
        "download": "/share/abc123token",
        "direct": "/file/abc123token",
        "preview": "/preview/abc123token"
      }
    }
  ],
  "total_files": 1
}
```

## 🔗 File Access URLs

### S3-Like Direct URLs

- **Direct Access:** `http://localhost:8000/file/{share_token}`
  - Serves file directly with proper MIME type
  - No authentication required for shareable links

- **Preview URL:** `http://localhost:8000/preview/{share_token}`
  - Opens file in browser (inline display)
  - Perfect for image previews

- **Download URL:** `http://localhost:8000/share/{share_token}`
  - Forces file download with attachment header

- **Thumbnail URL:** `http://localhost:8000/thumbnail/{thumbnail_filename}`
  - 300x300px JPEG thumbnails for images

## 🔧 Laravel Integration Examples

### Laravel Service Class

```php
<?php

namespace App\Services;

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class FileShareService
{
    private string $baseUrl;
    private string $apiKey;

    public function __construct()
    {
        $this->baseUrl = config('fileshare.base_url', 'http://localhost:8000');
        $this->apiKey = config('fileshare.api_key');
    }

    /**
     * Upload file from Laravel UploadedFile
     */
    public function uploadFile(UploadedFile $file, string $folderPath = ''): array
    {
        $response = Http::withHeaders([
            'X-API-Key' => $this->apiKey
        ])->attach(
            'file', file_get_contents($file->getPathname()), $file->getClientOriginalName()
        )->post($this->baseUrl . '/api/v1/upload', [
            'folder_path' => $folderPath,
            'generate_preview' => 'true'
        ]);

        if ($response->successful()) {
            return $response->json()['data'];
        }

        throw new \Exception('File upload failed: ' . $response->body());
    }

    /**
     * Upload file from base64 data
     */
    public function uploadBase64(string $base64Data, string $filename, string $folderPath = ''): array
    {
        // Remove data:image/jpeg;base64, prefix if present
        $base64Data = preg_replace('/^data:.*?;base64,/', '', $base64Data);

        $response = Http::withHeaders([
            'X-API-Key' => $this->apiKey,
            'Content-Type' => 'application/json'
        ])->post($this->baseUrl . '/api/v1/upload/base64', [
            'filename' => $filename,
            'file_data' => $base64Data,
            'folder_path' => $folderPath
        ]);

        if ($response->successful()) {
            return $response->json()['data'];
        }

        throw new \Exception('File upload failed: ' . $response->body());
    }

    /**
     * Get file list
     */
    public function getFiles(string $folderPath = ''): array
    {
        $response = Http::withHeaders([
            'X-API-Key' => $this->apiKey
        ])->get($this->baseUrl . '/api/v1/files', [
            'folder_path' => $folderPath
        ]);

        if ($response->successful()) {
            return $response->json()['files'];
        }

        throw new \Exception('Failed to get files: ' . $response->body());
    }

    /**
     * Get full URL for file access
     */
    public function getFileUrl(string $shareToken, string $type = 'direct'): string
    {
        $endpoints = [
            'direct' => '/file/',
            'preview' => '/preview/',
            'download' => '/share/',
        ];

        return $this->baseUrl . $endpoints[$type] . $shareToken;
    }
}
```

### Laravel Controller Example

```php
<?php

namespace App\Http\Controllers;

use App\Services\FileShareService;
use Illuminate\Http\Request;

class FileController extends Controller
{
    private FileShareService $fileShare;

    public function __construct(FileShareService $fileShare)
    {
        $this->fileShare = $fileShare;
    }

    public function upload(Request $request)
    {
        $request->validate([
            'file' => 'required|file|max:102400', // 100MB max
            'folder' => 'sometimes|string'
        ]);

        try {
            $fileData = $this->fileShare->uploadFile(
                $request->file('file'),
                $request->input('folder', 'uploads')
            );

            // Save file info to database
            $file = new \App\Models\UploadedFile([
                'filename' => $fileData['filename'],
                'original_name' => $fileData['original_name'],
                'folder_path' => $fileData['folder_path'],
                'size_bytes' => $fileData['size_bytes'],
                'md5' => $fileData['md5'],
                'share_token' => $fileData['share_token'],
                'direct_url' => $fileData['urls']['direct'],
                'preview_url' => $fileData['urls']['preview'],
                'thumbnail_url' => $fileData['urls']['thumbnail'],
                'upload_date' => $fileData['upload_date']
            ]);
            $file->save();

            return response()->json([
                'success' => true,
                'file' => $file,
                'urls' => $fileData['urls']
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => $e->getMessage()
            ], 500);
        }
    }

    public function uploadBase64(Request $request)
    {
        $request->validate([
            'image_data' => 'required|string',
            'filename' => 'required|string',
            'folder' => 'sometimes|string'
        ]);

        try {
            $fileData = $this->fileShare->uploadBase64(
                $request->input('image_data'),
                $request->input('filename'),
                $request->input('folder', 'images')
            );

            return response()->json([
                'success' => true,
                'data' => $fileData
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => $e->getMessage()
            ], 500);
        }
    }
}
```

### Laravel Migration Example

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('uploaded_files', function (Blueprint $table) {
            $table->id();
            $table->string('filename');
            $table->string('original_name');
            $table->string('folder_path')->nullable();
            $table->bigInteger('size_bytes');
            $table->string('md5');
            $table->string('share_token');
            $table->string('direct_url');
            $table->string('preview_url')->nullable();
            $table->string('thumbnail_url')->nullable();
            $table->timestamp('upload_date');
            $table->timestamps();
            
            $table->index(['folder_path', 'created_at']);
            $table->index('share_token');
        });
    }

    public function down()
    {
        Schema::dropIfExists('uploaded_files');
    }
};
```

### Laravel Configuration

Create `config/fileshare.php`:

```php
<?php

return [
    'base_url' => env('FILESHARE_BASE_URL', 'http://localhost:8000'),
    'api_key' => env('FILESHARE_API_KEY'),
];
```

Add to `.env`:
```
FILESHARE_BASE_URL=http://your-fileshare-server.com
FILESHARE_API_KEY=your-generated-api-key-here
```

## 🛡️ Security Features

- **API Key Authentication**: All endpoints require valid API keys
- **File Type Validation**: Only allowed extensions can be uploaded
- **Secure Filename Handling**: Filenames are sanitized
- **MD5 Checksums**: File integrity verification
- **Expiring Links**: Share links expire after 7 days by default
- **Rate Limiting**: Consider implementing rate limiting in production

## 📊 Response Codes

- `200` - Success
- `400` - Bad Request (missing parameters, invalid file type)
- `401` - Unauthorized (invalid/missing API key)
- `404` - File not found
- `410` - Link expired
- `500` - Server error

## 🔧 Configuration

### Admin Operations

Generate new API keys:
```bash
curl -X POST http://localhost:8000/api/v1/generate-key \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: your-admin-secret-key" \
  -d '{"name": "Production API Key"}'
```

**⚠️ Important:** Change the admin key in `app.py` from `'your-admin-secret-key'` to a secure value in production.

### File Organization

Files are organized in folder structures:
- Root uploads: `/uploads/filename.ext`
- Folder uploads: `/uploads/folder/subfolder/filename.ext`
- Thumbnails: `/thumbnails/thumb_filename.jpg`

This API provides S3-compatible functionality with additional features like real-time notifications, thumbnail generation, and flexible authentication options.

<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\FileShareService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

/**
 * Example Laravel Controller for FileShare Pro Integration
 */
class FileShareController extends Controller
{
    private FileShareService $fileShare;

    public function __construct(FileShareService $fileShare)
    {
        $this->fileShare = $fileShare;
    }

    /**
     * Upload a file to FileShare Pro
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function upload(Request $request): JsonResponse
    {
        $request->validate([
            'file' => 'required|file|max:102400', // 100MB max
            'folder' => 'sometimes|string|max:255',
            'generate_preview' => 'sometimes|boolean'
        ]);

        try {
            $fileData = $this->fileShare->uploadFile(
                $request->file('file'),
                $request->input('folder', 'uploads/' . date('Y/m'))
            );

            // Optionally save to your database
            $this->saveFileToDatabase($fileData);

            return response()->json([
                'success' => true,
                'message' => 'File uploaded successfully',
                'data' => [
                    'filename' => $fileData['filename'],
                    'urls' => $fileData['urls'],
                    'size' => $fileData['size_mb'] . ' MB',
                    'type' => $fileData['mime_type']
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Upload failed: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Upload image from base64 data
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function uploadBase64(Request $request): JsonResponse
    {
        $request->validate([
            'image_data' => 'required|string',
            'filename' => 'required|string|max:255',
            'folder' => 'sometimes|string|max:255'
        ]);

        try {
            // Remove data URL prefix if present
            $imageData = $request->input('image_data');
            if (strpos($imageData, 'data:') === 0) {
                $imageData = explode(',', $imageData, 2)[1];
            }

            $fileData = $this->fileShare->uploadBase64(
                $imageData,
                $request->input('filename'),
                $request->input('folder', 'images/' . date('Y/m'))
            );

            // Save to database
            $this->saveFileToDatabase($fileData);

            return response()->json([
                'success' => true,
                'message' => 'Image uploaded successfully',
                'data' => [
                    'preview_url' => $fileData['urls']['preview'],
                    'direct_url' => $fileData['urls']['direct'],
                    'thumbnail_url' => $fileData['urls']['thumbnail'],
                    'filename' => $fileData['filename']
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Upload failed: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get uploaded files
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function getFiles(Request $request): JsonResponse
    {
        try {
            $files = $this->fileShare->getFiles(
                $request->input('folder_path', '')
            );

            return response()->json([
                'success' => true,
                'files' => $files,
                'total' => count($files)
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Failed to get files: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Generate shareable link for existing file
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function generateShareLink(Request $request): JsonResponse
    {
        $request->validate([
            'share_token' => 'required|string',
            'expires_days' => 'sometimes|integer|min:1|max:365'
        ]);

        // This would call your FileShare Pro API to generate a new link
        // Implementation depends on your specific needs

        return response()->json([
            'success' => true,
            'message' => 'Share link generated',
            'share_url' => $this->fileShare->getFileUrl($request->input('share_token'), 'download')
        ]);
    }

    /**
     * Save file metadata to local database
     *
     * @param array $fileData
     * @return void
     */
    private function saveFileToDatabase(array $fileData): void
    {
        // Example: Save to a local files table
        // \App\Models\File::create([
        //     'filename' => $fileData['filename'],
        //     'original_name' => $fileData['original_name'],
        //     'folder_path' => $fileData['folder_path'],
        //     'size_bytes' => $fileData['size_bytes'],
        //     'md5' => $fileData['md5'],
        //     'share_token' => $fileData['share_token'],
        //     'direct_url' => $fileData['urls']['direct'],
        //     'preview_url' => $fileData['urls']['preview'],
        //     'thumbnail_url' => $fileData['urls']['thumbnail'],
        //     'mime_type' => $fileData['mime_type'],
        //     'uploaded_at' => now()
        // ]);
    }
}

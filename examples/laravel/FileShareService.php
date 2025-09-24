<?php

namespace App\Services;

use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

/**
 * FileShare Pro Service for Laravel Integration
 */
class FileShareService
{
    private string $baseUrl;
    private string $apiKey;
    private int $timeout;

    public function __construct()
    {
        $this->baseUrl = rtrim(config('fileshare.base_url', 'http://localhost:8000'), '/');
        $this->apiKey = config('fileshare.api_key');
        $this->timeout = config('fileshare.timeout', 30);

        if (empty($this->apiKey)) {
            throw new \Exception('FileShare API key is not configured');
        }
    }

    /**
     * Upload file from Laravel UploadedFile
     *
     * @param UploadedFile $file
     * @param string $folderPath
     * @param bool $generatePreview
     * @return array
     * @throws \Exception
     */
    public function uploadFile(
        UploadedFile $file, 
        string $folderPath = '', 
        bool $generatePreview = true
    ): array {
        try {
            $response = Http::timeout($this->timeout)
                ->withHeaders(['X-API-Key' => $this->apiKey])
                ->attach(
                    'file', 
                    file_get_contents($file->getPathname()), 
                    $file->getClientOriginalName()
                )
                ->post($this->baseUrl . '/api/v1/upload', [
                    'folder_path' => $folderPath,
                    'generate_preview' => $generatePreview ? 'true' : 'false'
                ]);

            if (!$response->successful()) {
                Log::error('FileShare upload failed', [
                    'status' => $response->status(),
                    'response' => $response->body()
                ]);
                throw new \Exception('File upload failed: ' . $response->json()['error'] ?? 'Unknown error');
            }

            return $response->json()['data'];

        } catch (\Illuminate\Http\Client\RequestException $e) {
            Log::error('FileShare API request failed', ['error' => $e->getMessage()]);
            throw new \Exception('File upload failed: Network error');
        }
    }

    /**
     * Upload file from base64 data
     *
     * @param string $base64Data
     * @param string $filename
     * @param string $folderPath
     * @return array
     * @throws \Exception
     */
    public function uploadBase64(string $base64Data, string $filename, string $folderPath = ''): array
    {
        try {
            // Clean base64 data - remove data URL prefix if present
            $base64Data = preg_replace('/^data:.*?;base64,/', '', $base64Data);

            $response = Http::timeout($this->timeout)
                ->withHeaders([
                    'X-API-Key' => $this->apiKey,
                    'Content-Type' => 'application/json'
                ])
                ->post($this->baseUrl . '/api/v1/upload/base64', [
                    'filename' => $filename,
                    'file_data' => $base64Data,
                    'folder_path' => $folderPath
                ]);

            if (!$response->successful()) {
                Log::error('FileShare base64 upload failed', [
                    'status' => $response->status(),
                    'response' => $response->body()
                ]);
                throw new \Exception('File upload failed: ' . $response->json()['error'] ?? 'Unknown error');
            }

            return $response->json()['data'];

        } catch (\Illuminate\Http\Client\RequestException $e) {
            Log::error('FileShare API request failed', ['error' => $e->getMessage()]);
            throw new \Exception('File upload failed: Network error');
        }
    }

    /**
     * Get list of files
     *
     * @param string $folderPath
     * @return array
     * @throws \Exception
     */
    public function getFiles(string $folderPath = ''): array
    {
        try {
            $response = Http::timeout($this->timeout)
                ->withHeaders(['X-API-Key' => $this->apiKey])
                ->get($this->baseUrl . '/api/v1/files', [
                    'folder_path' => $folderPath
                ]);

            if (!$response->successful()) {
                Log::error('FileShare get files failed', [
                    'status' => $response->status(),
                    'response' => $response->body()
                ]);
                throw new \Exception('Failed to get files: ' . $response->json()['error'] ?? 'Unknown error');
            }

            return $response->json()['files'];

        } catch (\Illuminate\Http\Client\RequestException $e) {
            Log::error('FileShare API request failed', ['error' => $e->getMessage()]);
            throw new \Exception('Failed to get files: Network error');
        }
    }

    /**
     * Get full URL for file access
     *
     * @param string $shareToken
     * @param string $type (direct|preview|download|thumbnail)
     * @return string
     */
    public function getFileUrl(string $shareToken, string $type = 'direct'): string
    {
        $endpoints = [
            'direct' => '/file/',
            'preview' => '/preview/',
            'download' => '/share/',
            'thumbnail' => '/thumbnail/'
        ];

        if (!isset($endpoints[$type])) {
            throw new \InvalidArgumentException("Invalid URL type: {$type}");
        }

        return $this->baseUrl . $endpoints[$type] . $shareToken;
    }

    /**
     * Check if FileShare Pro server is available
     *
     * @return bool
     */
    public function isServerAvailable(): bool
    {
        try {
            $response = Http::timeout(5)->get($this->baseUrl . '/');
            return $response->successful();
        } catch (\Exception $e) {
            return false;
        }
    }

    /**
     * Get server statistics
     *
     * @return array|null
     */
    public function getServerStats(): ?array
    {
        try {
            $response = Http::timeout($this->timeout)
                ->get($this->baseUrl . '/api/stats');

            if ($response->successful()) {
                return $response->json();
            }

            return null;
        } catch (\Exception $e) {
            Log::warning('Failed to get FileShare server stats', ['error' => $e->getMessage()]);
            return null;
        }
    }

    /**
     * Upload multiple files at once
     *
     * @param array $files Array of UploadedFile objects
     * @param string $folderPath
     * @return array
     */
    public function uploadMultipleFiles(array $files, string $folderPath = ''): array
    {
        $results = [];
        $errors = [];

        foreach ($files as $index => $file) {
            try {
                $result = $this->uploadFile($file, $folderPath);
                $results[] = $result;
            } catch (\Exception $e) {
                $errors[] = [
                    'file' => $file->getClientOriginalName(),
                    'error' => $e->getMessage()
                ];
            }
        }

        return [
            'successful_uploads' => $results,
            'failed_uploads' => $errors,
            'total_success' => count($results),
            'total_failed' => count($errors)
        ];
    }

    /**
     * Create a folder on the FileShare server
     *
     * @param string $folderPath
     * @return bool
     */
    public function createFolder(string $folderPath): bool
    {
        try {
            $response = Http::timeout($this->timeout)
                ->withHeaders([
                    'X-API-Key' => $this->apiKey,
                    'Content-Type' => 'application/json'
                ])
                ->post($this->baseUrl . '/api/create-folder', [
                    'folder_path' => $folderPath
                ]);

            return $response->successful();

        } catch (\Exception $e) {
            Log::error('Failed to create folder', [
                'folder_path' => $folderPath,
                'error' => $e->getMessage()
            ]);
            return false;
        }
    }
}

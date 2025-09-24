<?php

return [
    /*
    |--------------------------------------------------------------------------
    | FileShare Pro Configuration
    |--------------------------------------------------------------------------
    |
    | Configuration for FileShare Pro integration
    |
    */

    'base_url' => env('FILESHARE_BASE_URL', 'http://localhost:8000'),
    'api_key' => env('FILESHARE_API_KEY'),
    'timeout' => env('FILESHARE_TIMEOUT', 30), // seconds

    // Default folder for uploads
    'default_folder' => env('FILESHARE_DEFAULT_FOLDER', 'uploads'),

    // Whether to generate previews by default
    'generate_preview' => env('FILESHARE_GENERATE_PREVIEW', true),

    // Maximum file size in MB
    'max_file_size' => env('FILESHARE_MAX_SIZE', 100),

    // Allowed file extensions
    'allowed_extensions' => [
        'images' => ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'],
        'documents' => ['pdf', 'doc', 'docx', 'txt', 'rtf'],
        'spreadsheets' => ['xls', 'xlsx', 'csv'],
        'archives' => ['zip', 'rar', '7z'],
        'videos' => ['mp4', 'avi', 'mov', 'wmv'],
        'audio' => ['mp3', 'wav', 'flac', 'm4a']
    ]
];

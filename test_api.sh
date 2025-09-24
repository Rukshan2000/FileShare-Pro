#!/bin/bash

# FileShare Pro API Test Script
echo "🚀 Testing FileShare Pro API..."

# Base URL
BASE_URL="http://localhost:8000"

echo
echo "1. Generating API Key..."
API_RESPONSE=$(curl -s -X POST $BASE_URL/api/v1/generate-key \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: your-admin-secret-key" \
  -d '{"name": "Test API Key"}')

echo "API Key Response: $API_RESPONSE"

# Extract API key from response (requires jq)
if command -v jq &> /dev/null; then
    API_KEY=$(echo $API_RESPONSE | jq -r '.api_key // empty')
    if [ ! -z "$API_KEY" ]; then
        echo "✅ API Key generated: $API_KEY"

        echo
        echo "2. Testing file list endpoint..."
        curl -s -H "X-API-Key: $API_KEY" "$BASE_URL/api/v1/files" | jq '.' || echo "Files response received"

        echo
        echo "3. Testing Base64 upload..."
        # Create a simple test file
        echo "Hello World! This is a test file." > /tmp/test.txt
        BASE64_DATA=$(base64 -w 0 /tmp/test.txt)

        UPLOAD_RESPONSE=$(curl -s -X POST $BASE_URL/api/v1/upload/base64 \
          -H "Content-Type: application/json" \
          -H "X-API-Key: $API_KEY" \
          -d "{\"filename\": \"test.txt\", \"file_data\": \"$BASE64_DATA\", \"folder_path\": \"api-tests\"}")

        echo "Upload Response:"
        echo $UPLOAD_RESPONSE | jq '.' || echo $UPLOAD_RESPONSE

        # Extract URLs from response
        DIRECT_URL=$(echo $UPLOAD_RESPONSE | jq -r '.data.urls.direct // empty')
        if [ ! -z "$DIRECT_URL" ]; then
            echo
            echo "4. Testing direct file access..."
            echo "Direct URL: $BASE_URL$DIRECT_URL"
            curl -s "$BASE_URL$DIRECT_URL" | head -c 50
            echo " ..."
        fi

        echo
        echo "✅ API tests completed!"

    else
        echo "❌ Failed to extract API key from response"
    fi
else
    echo "⚠️  jq not found - install with: sudo apt-get install jq"
    echo "Raw API Key Response: $API_RESPONSE"
fi

echo
echo "📖 Available endpoints:"
echo "  - POST /api/v1/upload (multipart form)"
echo "  - POST /api/v1/upload/base64 (JSON)"
echo "  - GET  /api/v1/files"
echo "  - GET  /file/{token} (direct access)"
echo "  - GET  /preview/{token} (preview)"
echo "  - GET  /share/{token} (download)"
echo "  - GET  /thumbnail/{filename} (thumbnails)"
echo
echo "🌐 Server running at: $BASE_URL"
echo "📚 Full documentation: see API_DOCUMENTATION.md"

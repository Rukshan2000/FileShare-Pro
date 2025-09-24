// Professional File Sharing App JavaScript

// Socket.io connection
const socket = io();

// Global variables
let currentFiles = [];
let deleteModal = null;
let fileToDelete = null;

// Socket event handlers
socket.on('connected', (data) => {
    console.log('Connected to server:', data.message);
    addActivity('Connected to file sharing server');
});

socket.on('file_uploaded', (data) => {
    addActivity(`File uploaded: ${data.filename} (${data.size} MB)`);
    refreshFiles();
    updateStats();
});

socket.on('file_downloaded', (data) => {
    addActivity(`File downloaded: ${data.filename} (Total downloads: ${data.downloads})`);
    refreshFiles();
    updateStats();
});

socket.on('file_deleted', (data) => {
    addActivity(`File deleted: ${data.filename}`);
    refreshFiles();
    updateStats();
});

// Chat-specific socket handlers
socket.on('chat_history', (data) => {
    if (typeof displayChatHistory === 'function') {
        displayChatHistory(data.messages);
    }
});

socket.on('new_message', (data) => {
    if (typeof displayMessage === 'function') {
        displayMessage(data);
    }
});

socket.on('user_typing', (data) => {
    if (typeof showTypingIndicator === 'function') {
        showTypingIndicator(data.username);
    }
});

socket.on('user_stop_typing', (data) => {
    if (typeof hideTypingIndicator === 'function') {
        hideTypingIndicator(data.username);
    }
});

// Utility functions
function addActivity(message) {
    const activityLog = document.getElementById('activityLog');
    if (activityLog) {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `<i class="fas fa-info-circle"></i> ${new Date().toLocaleString()}: ${message}`;
        activityLog.prepend(activityItem);
        
        // Keep only the last 10 activities
        const activities = activityLog.children;
        if (activities.length > 10) {
            activityLog.removeChild(activities[activities.length - 1]);
        }
    }
}

async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        const totalFilesElem = document.getElementById('totalFiles');
        const totalDownloadsElem = document.getElementById('totalDownloads');
        const totalSizeElem = document.getElementById('totalSize');
        const fileCountElem = document.getElementById('fileCount');
        const totalSizeDisplayElem = document.getElementById('totalSizeDisplay');
        
        if (totalFilesElem) totalFilesElem.textContent = stats.total_files;
        if (totalDownloadsElem) totalDownloadsElem.textContent = stats.total_downloads;
        if (totalSizeElem) totalSizeElem.textContent = stats.total_size_mb + ' MB';
        if (fileCountElem) fileCountElem.textContent = stats.total_files;
        if (totalSizeDisplayElem) totalSizeDisplayElem.textContent = stats.total_size_mb + ' MB';
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// File management functions
async function refreshFiles() {
    try {
        const response = await fetch('/api/files');
        currentFiles = await response.json();
        displayFiles(currentFiles);
        updateStats();
    } catch (error) {
        console.error('Error refreshing files:', error);
        addActivity('Error refreshing file list');
    }
}

function displayFiles(files) {
    const tbody = document.getElementById('filesTableBody');
    const noFiles = document.getElementById('noFiles');
    
    if (!tbody) return;
    
    if (files.length === 0) {
        tbody.innerHTML = '';
        if (noFiles) noFiles.style.display = 'block';
        return;
    }
    
    if (noFiles) noFiles.style.display = 'none';
    
    tbody.innerHTML = files.map(file => `
        <tr>
            <td>
                <i class="fas fa-file"></i> 
                <span title="${file.name}">${file.name.length > 30 ? file.name.substring(0, 30) + '...' : file.name}</span>
            </td>
            <td>${file.size} MB</td>
            <td>${new Date(file.upload_date).toLocaleDateString()}</td>
            <td><span class="download-count">${file.downloads}</span></td>
            <td><small title="${file.md5}">${file.md5.substring(0, 8)}...</small></td>
            <td>
                <button class="btn btn-primary" onclick="downloadFile('${file.name.replace(/'/g, "\\'")}')">
                    <i class="fas fa-download"></i> Download
                </button>
                <button class="btn btn-danger" onclick="showDeleteModal('${file.name.replace(/'/g, "\\'")}')">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </td>
        </tr>
    `).join('');
}

async function downloadFile(filename) {
    try {
        // Create a temporary link to trigger download
        const link = document.createElement('a');
        link.href = `/api/download/${encodeURIComponent(filename)}`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        addActivity(`Download started: ${filename}`);
    } catch (error) {
        console.error('Error downloading file:', error);
        addActivity(`Download error: ${filename}`);
    }
}

// Upload modal functions
function showUploadModal(totalFiles, largeFiles) {
    // Create modal HTML
    const modalHTML = `
        <div id="uploadModal" class="upload-modal">
            <div class="upload-modal-content">
                <div class="upload-modal-header">
                    <h3><i class="fas fa-cloud-upload-alt"></i> Uploading Files</h3>
                </div>
                <div class="upload-modal-body">
                    <div class="upload-stats">
                        <div class="stat-item">
                            <i class="fas fa-files-o"></i>
                            <span>Total Files: <strong id="modalTotalFiles">${totalFiles}</strong></span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>Large Files: <strong id="modalLargeFiles">${largeFiles}</strong></span>
                        </div>
                    </div>
                    <div class="upload-progress-container">
                        <div class="progress-info">
                            <span id="currentFileName">Preparing upload...</span>
                            <span id="fileProgress">0/${totalFiles}</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-modal" id="modalProgressBar"></div>
                        </div>
                    </div>
                    <div class="upload-tips">
                        <p><i class="fas fa-info-circle"></i> Please keep this window open while files are uploading</p>
                        <p><i class="fas fa-clock"></i> Large files may take longer to upload</p>
                    </div>
                </div>
                <div class="upload-modal-footer">
                    <button class="btn btn-secondary" onclick="cancelUpload()" id="cancelUploadBtn">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Return modal element for reference
    return document.getElementById('uploadModal');
}

function updateUploadModalProgress(modal, current, total, filename) {
    if (!modal) return;
    
    const progressBar = modal.querySelector('#modalProgressBar');
    const currentFileName = modal.querySelector('#currentFileName');
    const fileProgress = modal.querySelector('#fileProgress');
    
    const progress = (current / total) * 100;
    
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
    
    if (currentFileName) {
        const displayName = filename.length > 30 ? filename.substring(0, 30) + '...' : filename;
        currentFileName.textContent = `Uploading: ${displayName}`;
    }
    
    if (fileProgress) {
        fileProgress.textContent = `${current}/${total}`;
    }
    
    // Change button to "Close" when upload is complete
    if (current === total) {
        const cancelBtn = modal.querySelector('#cancelUploadBtn');
        if (cancelBtn) {
            cancelBtn.innerHTML = '<i class="fas fa-check"></i> Close';
            cancelBtn.onclick = () => hideUploadModal(modal);
            cancelBtn.className = 'btn btn-primary';
        }
        
        if (currentFileName) {
            currentFileName.innerHTML = '<i class="fas fa-check-circle"></i> Upload Complete!';
        }
    }
}

function hideUploadModal(modal) {
    if (modal && modal.parentNode) {
        modal.style.animation = 'modalSlideOut 0.3s ease';
        setTimeout(() => {
            modal.parentNode.removeChild(modal);
        }, 300);
    }
}

function cancelUpload() {
    const modal = document.getElementById('uploadModal');
    if (modal) {
        // You could add cancel logic here if needed
        hideUploadModal(modal);
        addActivity('Upload cancelled by user');
    }
}

// Modal functions
function showDeleteModal(filename) {
    const modal = document.getElementById('deleteModal');
    const fileNameSpan = document.getElementById('deleteFileName');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    if (modal && fileNameSpan && confirmBtn) {
        fileToDelete = filename;
        fileNameSpan.textContent = filename;
        modal.style.display = 'flex';
        
        // Remove any existing event listeners and add new one
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        newConfirmBtn.addEventListener('click', confirmDelete);
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.style.display = 'none';
        fileToDelete = null;
    }
}

async function confirmDelete() {
    if (!fileToDelete) return;
    
    try {
        const response = await fetch(`/api/delete/${encodeURIComponent(fileToDelete)}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            addActivity(`File deleted: ${fileToDelete}`);
            refreshFiles();
            closeDeleteModal();
        } else {
            addActivity(`Delete failed: ${result.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error deleting file:', error);
        addActivity(`Delete error: ${fileToDelete}`);
    }
}

// Upload functionality
function setupUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    
    if (!uploadArea || !fileInput) return;
    
    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#ff6b6b';
        uploadArea.style.backgroundColor = 'rgba(255, 107, 107, 0.1)';
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        if (!uploadArea.contains(e.relatedTarget)) {
            uploadArea.style.borderColor = 'rgba(255, 255, 255, 0.3)';
            uploadArea.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        }
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'rgba(255, 255, 255, 0.3)';
        uploadArea.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
        handleFiles(e.dataTransfer.files);
    });
    
    // Click to select files
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

async function handleFiles(files) {
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    
    if (files.length === 0) return;
    
    // Check if any file is large (> 5MB) to show popup
    const largeFiles = Array.from(files).filter(file => file.size > 5 * 1024 * 1024);
    let uploadModal = null;
    
    if (largeFiles.length > 0) {
        uploadModal = showUploadModal(files.length, largeFiles.length);
    }
    
    // Show progress bar
    if (uploadProgress) {
        uploadProgress.style.display = 'block';
    }
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Update progress
        if (progressBar) {
            const progress = ((i + 1) / files.length) * 100;
            progressBar.style.width = `${progress}%`;
        }
        
        // Update modal progress if exists
        if (uploadModal) {
            updateUploadModalProgress(uploadModal, i + 1, files.length, file.name);
        }
        
        await uploadFile(file);
    }
    
    // Hide progress bar
    if (uploadProgress) {
        setTimeout(() => {
            uploadProgress.style.display = 'none';
            if (progressBar) progressBar.style.width = '0%';
        }, 1000);
    }
    
    // Hide upload modal
    if (uploadModal) {
        setTimeout(() => {
            hideUploadModal(uploadModal);
        }, 1500);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Show file size info for large files
        const fileSize = (file.size / (1024 * 1024)).toFixed(2);
        if (file.size > 5 * 1024 * 1024) {
            addActivity(`Uploading large file: ${file.name} (${fileSize} MB)`);
        } else {
            addActivity(`Uploading: ${file.name} (${fileSize} MB)`);
        }
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            addActivity(`✅ Upload successful: ${file.name} (${result.size} MB)`);
        } else {
            addActivity(`❌ Upload failed: ${file.name} - ${result.error}`);
        }
    } catch (error) {
        console.error('Upload error:', error);
        addActivity(`❌ Upload error: ${file.name} - Network error`);
    }
}

// Search functionality
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();
        
        if (searchTerm === '') {
            displayFiles(currentFiles);
        } else {
            const filteredFiles = currentFiles.filter(file => 
                file.name.toLowerCase().includes(searchTerm)
            );
            displayFiles(filteredFiles);
        }
    });
}

// Click outside modal to close
function setupModalClose() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeDeleteModal();
            }
        });
    }
    
    // ESC key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeDeleteModal();
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('File Sharing App initialized');
    
    // Setup file listing page
    if (document.getElementById('filesTableBody')) {
        refreshFiles();
        setupSearch();
        setupModalClose();
    }
    
    // Setup upload page
    if (document.getElementById('uploadArea')) {
        setupUpload();
    }
    
    // Setup stats on home page
    if (document.getElementById('totalFiles')) {
        updateStats();
        // Update stats every 10 seconds
        setInterval(updateStats, 10000);
    }
    
    // Setup chat page
    if (document.getElementById('chatMessages')) {
        setupChat();
    }
    
    // Add welcome message
    addActivity('File sharing application ready');
});

// Chat functionality
let currentUsername = '';
let typingTimeout = null;
let typingUsers = new Set();

function setupChat() {
    const usernameInput = document.getElementById('usernameInput');
    const joinChatBtn = document.getElementById('joinChatBtn');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const emojiBtn = document.getElementById('emojiBtn');
    const emojiPicker = document.getElementById('emojiPicker');
    const fileBtn = document.getElementById('fileBtn');
    const fileInput = document.getElementById('fileInput');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const cancelUploadBtn = document.getElementById('cancelUploadBtn');
    
    // Username setup
    joinChatBtn.addEventListener('click', joinChat);
    usernameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            joinChat();
        }
    });
    
    // Message sending
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // File upload functionality
    fileBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });
    
    // Drag and drop functionality
    const chatMain = document.getElementById('chatMain');
    if (chatMain) {
        chatMain.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadArea.style.display = 'block';
        });
        
        chatMain.addEventListener('dragleave', (e) => {
            if (!chatMain.contains(e.relatedTarget)) {
                fileUploadArea.style.display = 'none';
            }
        });
        
        chatMain.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadArea.style.display = 'none';
            
            if (e.dataTransfer.files.length > 0) {
                uploadFile(e.dataTransfer.files[0]);
            }
        });
    }
    
    // Cancel upload
    cancelUploadBtn.addEventListener('click', () => {
        fileUploadArea.style.display = 'none';
        if (window.currentUpload) {
            window.currentUpload.abort();
        }
    });
    
    // Typing indicators
    messageInput.addEventListener('input', () => {
        if (currentUsername) {
            socket.emit('user_typing', { username: currentUsername });
            
            // Clear previous timeout
            clearTimeout(typingTimeout);
            
            // Set new timeout to stop typing
            typingTimeout = setTimeout(() => {
                socket.emit('user_stop_typing', { username: currentUsername });
            }, 1000);
        }
    });
    
    // Emoji picker
    emojiBtn.addEventListener('click', toggleEmojiPicker);
    document.addEventListener('click', (e) => {
        if (!emojiPicker.contains(e.target) && !emojiBtn.contains(e.target)) {
            emojiPicker.style.display = 'none';
        }
    });
    
    // Emoji selection
    document.querySelectorAll('.emoji').forEach(emoji => {
        emoji.addEventListener('click', (e) => {
            const emojiChar = e.target.dataset.emoji;
            messageInput.value += emojiChar;
            messageInput.focus();
            emojiPicker.style.display = 'none';
        });
    });
    
    // Focus on username input
    usernameInput.focus();
}

function joinChat() {
    const usernameInput = document.getElementById('usernameInput');
    const username = usernameInput.value.trim();
    
    if (username && username.length >= 2) {
        currentUsername = username;
        document.getElementById('usernameSetup').style.display = 'none';
        document.getElementById('chatMain').style.display = 'flex';
        document.getElementById('messageInput').focus();
        
        // Add system message
        addSystemMessage(`${username} joined the chat`);
    } else {
        alert('Please enter a username (at least 2 characters)');
    }
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (message && currentUsername) {
        socket.emit('chat_message', {
            username: currentUsername,
            message: message
        });
        
        messageInput.value = '';
        
        // Stop typing indicator
        socket.emit('user_stop_typing', { username: currentUsername });
    }
}

function uploadFile(file) {
    if (!currentUsername) {
        alert('Please join the chat first');
        return;
    }
    
    // Check file size (max 100MB)
    if (file.size > 100 * 1024 * 1024) {
        alert('File size must be less than 100MB');
        return;
    }
    
    const fileUploadArea = document.getElementById('fileUploadArea');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const uploadInfo = document.getElementById('uploadInfo');
    
    // Show upload area
    fileUploadArea.style.display = 'block';
    uploadProgress.style.display = 'block';
    uploadInfo.style.display = 'none';
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('username', currentUsername);
    
    // Create XMLHttpRequest for progress tracking
    const xhr = new XMLHttpRequest();
    window.currentUpload = xhr;
    
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.style.width = percentComplete + '%';
            progressText.textContent = Math.round(percentComplete) + '%';
        }
    });
    
    xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            console.log('File uploaded successfully:', response);
        } else {
            const error = JSON.parse(xhr.responseText);
            alert('Upload failed: ' + error.error);
        }
        
        // Hide upload area
        fileUploadArea.style.display = 'none';
        progressBar.style.width = '0%';
        progressText.textContent = '0%';
        uploadProgress.style.display = 'none';
        uploadInfo.style.display = 'block';
        
        // Reset file input
        document.getElementById('fileInput').value = '';
    });
    
    xhr.addEventListener('error', () => {
        alert('Upload failed due to network error');
        fileUploadArea.style.display = 'none';
    });
    
    xhr.open('POST', '/api/chat/upload');
    xhr.send(formData);
}

function displayChatHistory(messages) {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '';
    
    messages.forEach(message => {
        displayMessage(message, false);
    });
    
    scrollToBottom();
}

function displayMessage(messageData, scroll = true) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const isOwnMessage = messageData.username === currentUsername;
    if (isOwnMessage) {
        messageDiv.classList.add('own-message');
    }
    
    // Add message type class
    if (messageData.type) {
        messageDiv.classList.add(`message-${messageData.type}`);
    }
    
    const timestamp = new Date(messageData.timestamp).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    let contentHtml = '';
    
    // Handle different message types
    switch (messageData.type) {
        case 'image':
            contentHtml = `
                <div class="message-header">
                    <span class="username">${escapeHtml(messageData.username)}</span>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="message-content">
                    <div class="file-message">
                        <div class="file-preview">
                            <img src="/api/download/${messageData.file_data.filename}" 
                                 alt="${escapeHtml(messageData.file_data.original_name)}" 
                                 class="image-preview" />
                        </div>
                        <div class="file-info">
                            <div class="file-name">${escapeHtml(messageData.file_data.original_name)}</div>
                            <div class="file-details">
                                ${messageData.file_data.size} MB
                                <a href="/api/download/${messageData.file_data.filename}" 
                                   download="${messageData.file_data.original_name}" 
                                   class="download-link">
                                    <i class="fas fa-download"></i> Download
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'file':
            const fileExtension = messageData.file_data.original_name.split('.').pop().toLowerCase();
            const fileIcon = getFileIcon(fileExtension);
            
            contentHtml = `
                <div class="message-header">
                    <span class="username">${escapeHtml(messageData.username)}</span>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="message-content">
                    <div class="file-message">
                        <div class="file-preview">
                            <i class="${fileIcon} file-icon"></i>
                        </div>
                        <div class="file-info">
                            <div class="file-name">${escapeHtml(messageData.file_data.original_name)}</div>
                            <div class="file-details">
                                ${messageData.file_data.size} MB
                                <a href="/api/download/${messageData.file_data.filename}" 
                                   download="${messageData.file_data.original_name}" 
                                   class="download-link">
                                    <i class="fas fa-download"></i> Download
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        default: // text message
            contentHtml = `
                <div class="message-header">
                    <span class="username">${escapeHtml(messageData.username)}</span>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="message-content">${escapeHtml(messageData.message)}</div>
            `;
            break;
    }
    
    messageDiv.innerHTML = contentHtml;
    chatMessages.appendChild(messageDiv);
    
    if (scroll) {
        scrollToBottom();
    }
}

function getFileIcon(extension) {
    const iconMap = {
        'pdf': 'fas fa-file-pdf',
        'doc': 'fas fa-file-word',
        'docx': 'fas fa-file-word',
        'xls': 'fas fa-file-excel',
        'xlsx': 'fas fa-file-excel',
        'txt': 'fas fa-file-alt',
        'zip': 'fas fa-file-archive',
        'mp4': 'fas fa-file-video',
        'mp3': 'fas fa-file-audio',
        'jpg': 'fas fa-file-image',
        'jpeg': 'fas fa-file-image',
        'png': 'fas fa-file-image',
        'gif': 'fas fa-file-image'
    };
    
    return iconMap[extension] || 'fas fa-file';
}

function addSystemMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system-message';
    
    const timestamp = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="fas fa-info-circle"></i>
            ${escapeHtml(message)}
            <span class="timestamp">${timestamp}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator(username) {
    if (username === currentUsername) return;
    
    typingUsers.add(username);
    updateTypingIndicator();
}

function hideTypingIndicator(username) {
    typingUsers.delete(username);
    updateTypingIndicator();
}

function updateTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    
    if (typingUsers.size === 0) {
        typingIndicator.style.display = 'none';
    } else {
        const usernames = Array.from(typingUsers);
        let text = '';
        
        if (usernames.length === 1) {
            text = `${usernames[0]} is typing...`;
        } else if (usernames.length === 2) {
            text = `${usernames[0]} and ${usernames[1]} are typing...`;
        } else {
            text = `${usernames.length} people are typing...`;
        }
        
        typingIndicator.innerHTML = `
            <div class="typing-dots">
                <i class="fas fa-ellipsis-h"></i>
                ${escapeHtml(text)}
            </div>
        `;
        typingIndicator.style.display = 'block';
    }
}

function toggleEmojiPicker() {
    const emojiPicker = document.getElementById('emojiPicker');
    emojiPicker.style.display = emojiPicker.style.display === 'none' ? 'block' : 'none';
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export functions for global use
window.refreshFiles = refreshFiles;
window.downloadFile = downloadFile;
window.showDeleteModal = showDeleteModal;
window.closeDeleteModal = closeDeleteModal;
window.displayChatHistory = displayChatHistory;
window.displayMessage = displayMessage;
window.showTypingIndicator = showTypingIndicator;
window.hideTypingIndicator = hideTypingIndicator;
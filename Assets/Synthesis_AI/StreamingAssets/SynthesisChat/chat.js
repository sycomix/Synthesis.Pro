// Synthesis AI Chat - JavaScript

// State
let messageHistory = [];
let isWaitingForResponse = false;

// DOM Elements
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const settingsBtn = document.getElementById('settingsBtn');
const statusElement = document.getElementById('status');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Synthesis Chat initialized');
    
    // Setup event listeners
    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', clearChat);
    settingsBtn.addEventListener('click', showSettings);
    
    // Handle Enter key
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
    
    // Check Unity bridge
    if (window.UnityChatBridge) {
        console.log('✅ Unity Chat Bridge detected');
    } else {
        console.log('⏳ Waiting for Unity Chat Bridge...');
        // The bridge will be injected by Unity after page load
        setTimeout(() => {
            if (window.UnityChatBridge) {
                console.log('✅ Unity Chat Bridge connected');
            }
        }, 1000);
    }
});

// Send message
function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isWaitingForResponse) {
        return;
    }
    
    // Add user message to UI
    addMessageToChat('You', message);
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Send to Unity
    if (window.UnityChatBridge && window.UnityChatBridge.sendMessage) {
        const success = window.UnityChatBridge.sendMessage(message);
        if (success) {
            // Show typing indicator
            showTypingIndicator();
        } else {
            console.error('❌ Failed to send message to Unity');
        }
    } else {
        console.error('❌ Unity Chat Bridge not available');
        addMessageToChat('System', '❌ Connection to Unity lost. Please restart the chat window.');
    }
}

// Add message to chat UI
function addMessageToChat(sender, message, timestamp = null) {
    // Remove welcome message if it exists
    const welcomeMessage = messagesContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    // Remove typing indicator if showing
    removeTypingIndicator();
    
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender === 'You' ? 'user' : 'ai'}`;
    
    const avatar = sender === 'You' ? '👤' : '🤖';
    const time = timestamp || new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-sender">${sender}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-bubble">${escapeHtml(message)}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    
    // Store in history
    messageHistory.push({ sender, message, timestamp: time });
    
    // Scroll to bottom
    scrollToBottom();
    
    // Update state
    isWaitingForResponse = false;
    updateSendButton();
}

// Show typing indicator
function showTypingIndicator() {
    isWaitingForResponse = true;
    updateSendButton();
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-bubble">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    isWaitingForResponse = false;
    updateSendButton();
}

// Update send button state
function updateSendButton() {
    sendBtn.disabled = isWaitingForResponse || !messageInput.value.trim();
}

// Clear chat
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        messageHistory = [];
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">👋</div>
                <h2>Chat Cleared!</h2>
                <p>Ready for a fresh start. How can I help you today?</p>
            </div>
        `;
        console.log('🗑️ Chat cleared');
    }
}

// Show settings (placeholder)
function showSettings() {
    alert('Settings coming soon!\n\n' +
          'Future features:\n' +
          '• Theme customization\n' +
          '• Font size adjustment\n' +
          '• Keyboard shortcuts\n' +
          '• Export chat history');
}

// Utility: Scroll to bottom
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Global function for Unity to call
window.addMessageToChat = addMessageToChat;

// Handle visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('📱 Chat window hidden');
    } else {
        console.log('👁️ Chat window visible');
    }
});

// Log ready state
console.log('✅ Synthesis Chat ready!');

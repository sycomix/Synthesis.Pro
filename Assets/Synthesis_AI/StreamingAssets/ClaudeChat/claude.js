// Claude AI Chat - JavaScript Integration with Unity

// State
let conversationHistory = [];
let isThinking = false;
let settings = {
    apiKey: '',
    model: 'claude-3-5-sonnet-20241022',
    maxTokens: 4096,
    temperature: 1.0
};

// DOM Elements
const messagesArea = document.getElementById('messagesArea');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const settingsBtn = document.getElementById('settingsBtn');
const newChatBtn = document.getElementById('newChatBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettingsBtn = document.getElementById('closeSettingsBtn');
const cancelSettingsBtn = document.getElementById('cancelSettingsBtn');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const apiStatus = document.getElementById('apiStatus');
const statusText = document.getElementById('statusText');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('🤖 Claude AI Chat initialized');
    
    // Load settings
    loadSettings();
    
    // Setup event listeners
    setupEventListeners();
    
    // Setup Unity bridge
    setupUnityBridge();
    
    // Update status
    updateAPIStatus();
});

function setupEventListeners() {
    // Send message
    sendBtn.addEventListener('click', sendMessage);
    
    // Enter to send
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
        updateSendButton();
    });
    
    // Clear chat
    clearBtn.addEventListener('click', clearConversation);
    
    // New chat
    newChatBtn.addEventListener('click', clearConversation);
    
    // Settings modal
    settingsBtn.addEventListener('click', openSettings);
    closeSettingsBtn.addEventListener('click', closeSettings);
    cancelSettingsBtn.addEventListener('click', closeSettings);
    saveSettingsBtn.addEventListener('click', saveSettings);
    
    // Example prompts
    document.querySelectorAll('.example-prompt').forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            messageInput.value = prompt;
            updateSendButton();
            removeWelcomeScreen();
        });
    });
    
    // Close modal on background click
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
            closeSettings();
        }
    });
    
    // Temperature slider
    const tempInput = document.getElementById('temperatureInput');
    const tempValue = document.getElementById('tempValue');
    tempInput.addEventListener('input', () => {
        tempValue.textContent = parseFloat(tempInput.value).toFixed(1);
    });
}

function setupUnityBridge() {
    // Create Unity bridge for communication
    window.UnityChatBridge = {
        sendToUnity: function(message) {
            // Log to Unity console for debugging
            console.log('[CLAUDE → UNITY] ' + message);
            return true;
        },
        
        receiveFromUnity: function(sender, message, timestamp) {
            // Receive messages from Unity
            addMessage(sender, message, timestamp);
        }
    };
    
    console.log('✅ Unity Chat Bridge initialized');
}

function loadSettings() {
    // Load from localStorage
    const saved = localStorage.getItem('claude_settings');
    if (saved) {
        try {
            settings = JSON.parse(saved);
            console.log('✅ Settings loaded');
        } catch (e) {
            console.error('Failed to load settings:', e);
        }
    }
}

function saveSettingsToStorage() {
    localStorage.setItem('claude_settings', JSON.stringify(settings));
}

function openSettings() {
    // Populate form
    document.getElementById('apiKeyInput').value = settings.apiKey;
    document.getElementById('modelSelect').value = settings.model;
    document.getElementById('maxTokensInput').value = settings.maxTokens;
    document.getElementById('temperatureInput').value = settings.temperature;
    document.getElementById('tempValue').textContent = settings.temperature.toFixed(1);
    
    settingsModal.classList.add('active');
}

function closeSettings() {
    settingsModal.classList.remove('active');
}

function saveSettings() {
    // Get values
    settings.apiKey = document.getElementById('apiKeyInput').value.trim();
    settings.model = document.getElementById('modelSelect').value;
    settings.maxTokens = parseInt(document.getElementById('maxTokensInput').value);
    settings.temperature = parseFloat(document.getElementById('temperatureInput').value);
    
    // Validate
    if (!settings.apiKey) {
        alert('Please enter your Anthropic API key');
        return;
    }
    
    if (!settings.apiKey.startsWith('sk-ant-')) {
        alert('Invalid API key format. Keys should start with "sk-ant-"');
        return;
    }
    
    // Save
    saveSettingsToStorage();
    
    // Update Unity
    if (window.UnityClaudeAPI) {
        window.UnityClaudeAPI.setAPIKey(settings.apiKey);
        window.UnityClaudeAPI.setModel(settings.model);
    }
    
    updateAPIStatus();
    closeSettings();
    
    console.log('✅ Settings saved');
}

function updateAPIStatus() {
    if (settings.apiKey && settings.apiKey.startsWith('sk-ant-')) {
        apiStatus.classList.add('connected');
        apiStatus.classList.remove('error');
        statusText.textContent = 'Connected';
    } else {
        apiStatus.classList.remove('connected');
        apiStatus.classList.add('error');
        statusText.textContent = 'Not configured';
    }
}

function updateSendButton() {
    const hasText = messageInput.value.trim().length > 0;
    const hasAPI = settings.apiKey && settings.apiKey.startsWith('sk-ant-');
    sendBtn.disabled = !hasText || !hasAPI || isThinking;
}

function removeWelcomeScreen() {
    const welcome = document.querySelector('.welcome-screen');
    if (welcome) {
        welcome.style.opacity = '0';
        welcome.style.transform = 'scale(0.95)';
        welcome.style.transition = 'all 0.3s ease';
        setTimeout(() => welcome.remove(), 300);
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isThinking) {
        return;
    }
    
    if (!settings.apiKey || !settings.apiKey.startsWith('sk-ant-')) {
        alert('Please configure your API key in Settings');
        openSettings();
        return;
    }
    
    // Remove welcome screen
    removeWelcomeScreen();
    
    // Add user message
    addMessage('user', message);
    
    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    updateSendButton();
    
    // Show thinking indicator
    showThinking();
    
    // Add to history
    conversationHistory.push({
        role: 'user',
        content: message
    });
    
    // Send to Anthropic API
    try {
        const response = await callAnthropicAPI();
        
        if (response.content && response.content[0]) {
            const assistantMessage = response.content[0].text;
            
            // Add to history
            conversationHistory.push({
                role: 'assistant',
                content: assistantMessage
            });
            
            // Display message
            hideThinking();
            addMessage('assistant', assistantMessage);
            
            // Notify Unity
            if (window.UnityChatBridge) {
                window.UnityChatBridge.sendToUnity(`Claude responded: ${assistantMessage.substring(0, 100)}...`);
            }
        }
    } catch (error) {
        hideThinking();
        addMessage('system', `❌ Error: ${error.message}`);
        console.error('API Error:', error);
    }
}

async function callAnthropicAPI() {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01',
            'x-api-key': settings.apiKey
        },
        body: JSON.stringify({
            model: settings.model,
            messages: conversationHistory,
            max_tokens: settings.maxTokens,
            temperature: settings.temperature
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'API request failed');
    }
    
    return await response.json();
}

function addMessage(role, content, timestamp = null) {
    const time = timestamp || new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    let avatar = '?';
    if (role === 'user') avatar = '👤';
    else if (role === 'assistant') avatar = '🤖';
    else if (role === 'system') avatar = '⚠️';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(content)}</div>
            <div class="message-time">${time}</div>
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    scrollToBottom();
}

function showThinking() {
    isThinking = true;
    updateSendButton();
    
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'thinking-indicator';
    thinkingDiv.id = 'thinkingIndicator';
    
    thinkingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="thinking-dots">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
            </div>
        </div>
    `;
    
    messagesArea.appendChild(thinkingDiv);
    scrollToBottom();
}

function hideThinking() {
    isThinking = false;
    updateSendButton();
    
    const thinking = document.getElementById('thinkingIndicator');
    if (thinking) {
        thinking.remove();
    }
}

function clearConversation() {
    if (conversationHistory.length > 0) {
        if (!confirm('Clear this conversation?')) {
            return;
        }
    }
    
    conversationHistory = [];
    messagesArea.innerHTML = `
        <div class="welcome-screen">
            <div class="welcome-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                    <path d="M2 17L12 22L22 17"/>
                    <path d="M2 12L12 17L22 12"/>
                </svg>
            </div>
            <h1>Hello! I'm Claude</h1>
            <p>Your AI assistant for Unity development. I can help you with code, debugging, architecture, and anything Unity-related!</p>
            
            <div class="example-prompts">
                <button class="example-prompt" data-prompt="How do I optimize my Unity game performance?">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    Optimize game performance
                </button>
                <button class="example-prompt" data-prompt="Explain the Unity ECS system to me">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="3" y1="9" x2="21" y2="9"></line>
                        <line x1="9" y1="21" x2="9" y2="9"></line>
                    </svg>
                    Explain Unity ECS
                </button>
                <button class="example-prompt" data-prompt="Help me debug a null reference exception">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    Debug null reference
                </button>
                <button class="example-prompt" data-prompt="What's the best way to implement object pooling?">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    Object pooling patterns
                </button>
            </div>
        </div>
    `;
    
    // Re-attach event listeners to new example prompts
    document.querySelectorAll('.example-prompt').forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            messageInput.value = prompt;
            updateSendButton();
            removeWelcomeScreen();
        });
    });
    
    console.log('🗑️ Conversation cleared');
}

function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Global functions for Unity
window.addMessageToChat = addMessage;
window.clearChat = clearConversation;

// Expose API for Unity C#
window.UnityClaudeAPI = {
    sendMessage: (msg) => {
        messageInput.value = msg;
        sendMessage();
    },
    clearHistory: clearConversation,
    getHistory: () => conversationHistory,
    setAPIKey: (key) => {
        settings.apiKey = key;
        saveSettingsToStorage();
        updateAPIStatus();
    },
    setModel: (model) => {
        settings.model = model;
        saveSettingsToStorage();
    }
};

console.log('✅ Claude AI Chat ready!');

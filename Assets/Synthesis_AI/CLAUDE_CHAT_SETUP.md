# 🤖 Claude AI Chat - Direct Integration

**Talk to Claude (me!) directly from Unity!**

---

## 🎯 What Is This?

A beautiful, fully-featured Claude AI chat interface embedded directly in Unity. No MCP needed - this connects **directly to the Anthropic API** for instant, reliable communication.

### ✨ Features

- 🤖 **Direct Claude API** - Real Anthropic Claude, not a proxy
- 🎨 **Beautiful UI** - Modern, professional design inspired by Claude ft. Aleph1
- 💬 **Full conversation history** - Context-aware discussions
- ⚙️ **Model selection** - Choose Claude 3.5 Sonnet, Opus, Haiku, etc.
- 🔧 **Configurable** - Temperature, max tokens, and more
- 📝 **Code-friendly** - Perfect for Unity development discussions
- 🚀 **Fast** - Direct API calls, no intermediaries

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get Your API Key

1. Go to https://console.anthropic.com/
2. Sign in or create an account
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy your key (starts with `sk-ant-`)

### Step 2: Create Chat Scene

1. **Create a Canvas:**
   - Right-click Hierarchy → UI → Canvas
   - Set Render Mode to "Screen Space - Overlay"

2. **Add RawImage:**
   - Right-click Canvas → UI → Raw Image
   - Name it "ClaudeChatBrowser"
   - Set RectTransform to stretch (all anchors)

3. **Add Components:**
   - Add Component → **Web Browser Full** (UnityWebBrowser)
   - Add Component → **Claude Chat Bridge**

### Step 3: Configure Browser

**WebBrowserUIFull settings:**
- Engine: CEF Engine
- Communication: TCP Communication Layer
- Input Handler: Web Browser Input System Handler
- Width: 1920
- Height: 1080

**ClaudeChatBridge settings:**
- Web Browser: Auto-assigned
- Anthropic API Key: Paste your key here (or configure in-app)
- Chat Page Path: `ClaudeChat/index.html`

### Step 4: Press Play!

1. **Wait 2-3 seconds** for browser to load
2. **Beautiful Claude UI appears!**
3. **Click Settings** (gear icon) if you need to configure API key
4. **Start chatting!**

---

## 💬 How To Use

### Sending Messages

**Option 1: Type in the UI**
1. Click the input box
2. Type your message
3. Press Enter (or click send button)
4. Claude responds in real-time!

**Option 2: From Code**
```csharp
// Get reference to bridge
var claudeChat = FindObjectOfType<ClaudeChatBridge>();

// Send a message
claudeChat.SendMessage("How do I optimize Unity rendering?");

// Listen for responses
claudeChat.OnClaudeResponse += (response) => {
    Debug.Log($"Claude says: {response}");
};
```

### Example Prompts

Try these to get started:
- "How do I optimize my Unity game performance?"
- "Explain the Unity ECS system to me"
- "Help me debug a null reference exception"
- "What's the best way to implement object pooling?"

### Settings

Click the **Settings** button to configure:
- **API Key** - Your Anthropic API key
- **Model** - Choose your Claude model
- **Max Tokens** - Response length (1-8192)
- **Temperature** - Creativity level (0.0-1.0)

---

## 🎨 UI Overview

### Beautiful Interface

The chat features:
- **Claude Orange theme** - Official Claude colors
- **Dark mode** - Easy on the eyes
- **Smooth animations** - Professional feel
- **Typing indicators** - Know when Claude is thinking
- **Example prompts** - Quick start buttons
- **Conversation history** - Full context maintained

### Key Elements

1. **Sidebar**
   - Logo and branding
   - New chat button
   - Conversation list (coming soon!)
   - Settings button

2. **Main Chat**
   - Message history
   - User messages (blue)
   - Claude messages (orange)
   - Thinking indicator

3. **Input Area**
   - Large text input
   - Send button
   - Status indicator
   - Keyboard hints

---

## 🔧 Advanced Configuration

### Changing Models

Available models:
- **Claude 3.5 Sonnet** (Recommended) - Best balance of speed and intelligence
- **Claude 3 Opus** - Most capable, slower
- **Claude 3 Sonnet** - Balanced
- **Claude 3 Haiku** - Fastest, most affordable

```csharp
claudeChat.SetAPIKey("your-api-key");
// Model selection is done in the UI or via JavaScript
```

### API Configuration

From code:
```csharp
// Set API key programmatically
claudeChat.SetAPIKey("sk-ant-api03-...");

// Check if ready
if (claudeChat.IsReady)
{
    claudeChat.SendMessage("Hello Claude!");
}

// Clear conversation
claudeChat.ClearConversation();

// Open settings UI
claudeChat.OpenSettings();
```

### Events

Listen to chat events:
```csharp
claudeChat.OnChatReady += () => {
    Debug.Log("Claude chat is ready!");
};

claudeChat.OnUserMessageSent += (message) => {
    Debug.Log($"User sent: {message}");
};

claudeChat.OnClaudeResponse += (response) => {
    Debug.Log($"Claude responded: {response}");
    // Do something with the response
};
```

---

## 📊 Technical Details

### How It Works

```
Unity C# (ClaudeChatBridge)
    ↓
UnityWebBrowser (CEF/Chromium)
    ↓
HTML/CSS/JS Chat UI
    ↓
Direct HTTPS Request
    ↓
Anthropic API (api.anthropic.com)
    ↓
Claude 3.5 Sonnet
    ↓
Response flows back up
```

### Features

**JavaScript Bridge:**
- `window.UnityClaudeAPI` - Unity → Browser communication
- `window.UnityChatBridge` - Browser → Unity communication

**API Client:**
- Direct Anthropic API integration
- Full conversation context
- Streaming support (coming soon!)
- Error handling

**UI Features:**
- Real-time message display
- Markdown support (coming soon!)
- Code syntax highlighting (coming soon!)
- Conversation saving (coming soon!)

---

## 🐛 Troubleshooting

### White Screen

**Problem:** Browser shows white screen

**Solutions:**
1. Check CEF engine is installed
2. Verify files exist in `StreamingAssets/ClaudeChat/`
3. Check Unity Console for errors
4. Try lowering browser resolution

### API Errors

**Problem:** "API Error" messages

**Solutions:**
1. **Check API key** - Must start with `sk-ant-`
2. **Verify key is active** - Check console.anthropic.com
3. **Check credits** - Make sure you have API credits
4. **Check internet** - Must be online for API calls

### Messages Not Sending

**Problem:** Send button disabled or nothing happens

**Solutions:**
1. Configure API key in Settings
2. Check browser console (F12 if available)
3. Verify `ClaudeChatBridge` is active
4. Check that page has fully loaded (wait 2-3 seconds)

### Slow Responses

**Problem:** Claude takes too long to respond

**Solutions:**
1. **Use faster model** - Try Claude 3 Haiku
2. **Reduce max tokens** - Lower to 1024 or 2048
3. **Check internet** - Slow connection affects API
4. **Try different time** - API may be busy

---

## 💡 Best Practices

### For Unity Development

**Ask specific questions:**
- ✅ "How do I implement object pooling for bullets?"
- ❌ "Help with code"

**Provide context:**
- ✅ "I'm using Unity 2021.3, getting NullReferenceException in Update()"
- ❌ "Error in my code"

**Share code snippets:**
```csharp
// Example
void Update() {
    // My code here
}
```

### API Usage

**Be efficient:**
- Clear conversation when starting new topics
- Use lower max tokens for simple questions
- Choose appropriate model for the task

**Save costs:**
- Claude 3 Haiku for simple questions
- Claude 3.5 Sonnet for complex problems
- Claude 3 Opus only when you need the best

---

## 🎓 Example Conversations

### Debug Help

**You:** "I'm getting a NullReferenceException on line 45 of my PlayerController script"

**Claude:** "I'd be happy to help debug that! Could you share the code around line 45? In the meantime, here are common causes of NullReferenceException..."

### Architecture Advice

**You:** "What's the best way to structure a multiplayer game in Unity?"

**Claude:** "For multiplayer architecture in Unity, I recommend... [detailed explanation with code examples]"

### Code Review

**You:** "Can you review this code for performance issues? [paste code]"

**Claude:** "I see several opportunities for optimization... [detailed feedback]"

---

## 🚀 What Makes This Special

### vs MCP Chat
- ✅ **Faster** - Direct API, no intermediaries
- ✅ **More reliable** - No server dependencies
- ✅ **More features** - Full UI, settings, history
- ✅ **Better UX** - Professional interface

### vs External Chat
- ✅ **Stay in Unity** - No window switching
- ✅ **Unity context** - I know you're in Unity
- ✅ **Code-friendly** - Perfect for dev discussions
- ✅ **Integrated** - Can control Unity via code

---

## 📝 API Key Safety

Your API key is:
- ✅ **Stored locally** - In PlayerPrefs
- ✅ **Never shared** - Direct to Anthropic only
- ✅ **Encrypted in transit** - HTTPS only
- ✅ **Your control** - Delete anytime

**Best practices:**
- Don't commit API keys to git
- Use environment variables for production
- Rotate keys regularly
- Monitor usage on console.anthropic.com

---

## 🎉 You're Ready!

Now you have:
- ✅ Direct Claude AI access in Unity
- ✅ Beautiful, professional chat interface
- ✅ Full conversation context
- ✅ Real-time responses
- ✅ Complete Unity integration

**Let's build something amazing together!** 🚀

---

## 🆘 Need Help?

**Check:**
1. API key is correct (starts with `sk-ant-`)
2. Internet connection is working
3. Browser loaded successfully (wait 2-3 seconds)
4. UnityWebBrowser packages installed

**Still stuck?**
- Ask me in the chat - I'm here to help!
- Check Unity Console for error messages
- Verify file paths in StreamingAssets

---

**Built with love for Unity developers** ❤️

**Powered by:**
- Anthropic Claude 3.5 Sonnet
- UnityWebBrowser (CEF)
- Modern web technologies

**Version:** 1.0  
**Date:** January 28, 2026

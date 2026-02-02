# AI Chat Bridge Setup Guide

## What is This?

The **AI Chat Bridge** is a standalone Python application that provides real-time AI assistance in Unity. It works with multiple AI providers (Anthropic Claude, OpenAI GPT, Ollama, etc.) and requires no IDE - just Python and an API key!

## Features

✅ **Provider Agnostic** - Works with Anthropic, OpenAI, Ollama, and more  
✅ **Standalone** - No IDE required (works in Edit Mode!)  
✅ **Real-time** - Instant responses via Unity's web chat  
✅ **Conversation Memory** - Remembers context across messages  
✅ **Knowledge Base Integration** - Shares context with Cursor AI!  
✅ **Universal** - Works on any Unity project  

---

## Quick Start

### 1. Install Dependencies

Run the setup script:
```bash
Assets\Synthesis_Package\setup_ai_bridge.bat
```

This installs:
- `anthropic` (for Claude)
- `openai` (for GPT)
- `requests` (for HTTP)

### 2. Configure Your API Key

A config file will be created at: `Assets/Synthesis_Package/ai_config.json`

Edit it and add your API key:

```json
{
  "provider": "anthropic",
  "anthropic": {
    "api_key": "sk-ant-YOUR_KEY_HERE",
    "model": "claude-3-5-sonnet-20241022"
  },
  "openai": {
    "api_key": "YOUR_OPENAI_KEY_HERE",
    "model": "gpt-4"
  },
  "ollama": {
    "endpoint": "http://localhost:11434",
    "model": "llama2"
  }
}
```

### 3. Start the Bridge

Run the launcher:
```bash
Assets\Synthesis_Package\start_ai_bridge.bat
```

Or manually:
```bash
KnowledgeBase\python\python.exe Assets\Synthesis_Package\ai_chat_bridge.py
```

### 4. Chat in Unity!

- Open Unity (Edit Mode works!)
- The HTTP server starts automatically
- Open the web chat or use the chat window
- Type messages - AI responds automatically!

---

## 🧠 Knowledge Base Integration

**The AI Bridge automatically shares context with Cursor AI via the Knowledge Base!**

### How It Works:

1. **Cursor AI (you)** works on code and adds knowledge to the KB
2. **Bridge AI** reads the KB before responding to Unity questions
3. **Bridge AI** saves conversations back to the KB
4. **Both AIs** learn from each other over time!

### Benefits:

- ✅ Bridge AI knows your project architecture
- ✅ Consistent answers between Cursor and Unity chat
- ✅ All conversations saved for future reference
- ✅ Self-learning system that improves over time

### Setup:

If you haven't set up the Knowledge Base yet:
```bash
KnowledgeBase\setup_kb.bat
```

The AI Bridge will automatically:
- Load relevant project docs when answering questions
- Save all conversations to `ai_conversations` table
- Use KB context to give smarter answers

---

## Supported Providers

### Anthropic Claude (Recommended)
- **Best for:** General development, coding, Unity help
- **Cost:** ~$3 per 1M input tokens, $15 per 1M output tokens
- **Get Key:** https://console.anthropic.com/
- **Set in config:**
  ```json
  "provider": "anthropic",
  "anthropic": {
    "api_key": "sk-ant-...",
    "model": "claude-3-5-sonnet-20241022"
  }
  ```

### OpenAI GPT
- **Best for:** General purpose, multilingual
- **Cost:** Varies by model
- **Get Key:** https://platform.openai.com/
- **Set in config:**
  ```json
  "provider": "openai",
  "openai": {
    "api_key": "sk-...",
    "model": "gpt-4"
  }
  ```

### Ollama (Local/Free)
- **Best for:** Privacy, offline work, no API costs
- **Cost:** FREE (but requires good hardware)
- **Setup:** Install Ollama from https://ollama.ai/
- **Set in config:**
  ```json
  "provider": "ollama",
  "ollama": {
    "endpoint": "http://localhost:11434",
    "model": "llama2"
  }
  ```

---

## Configuration Options

```json
{
  "provider": "anthropic",  // Which AI provider to use
  
  "unity": {
    "http_port": 9765  // Unity HTTP server port
  },
  
  "settings": {
    "check_interval": 2,  // How often to check for messages (seconds)
    "max_context_messages": 10  // How many messages to remember
  }
}
```

---

## Troubleshooting

### "Cannot connect to Unity"
- Make sure Unity is running
- Check that SynLink servers started (look for `[SynLink] 🔗 HTTP Server started on port 9765`)
- Verify `http_port` in config matches Unity's server port

### "Error: API key not set"
- Edit `ai_config.json` and add your API key
- Remove "YOUR_..._KEY_HERE" placeholder text

### "Package not installed" errors
- Run `setup_ai_bridge.bat` again
- Or manually: `KnowledgeBase\python\python.exe -m pip install anthropic openai requests`

### Ollama connection errors
- Make sure Ollama is running: `ollama serve`
- Check endpoint URL in config
- Test manually: `curl http://localhost:11434/api/tags`

---

## For Developers

### Adding New Providers

Edit `ai_chat_bridge.py` and add a new method to the `AIProvider` class:

```python
def _call_your_provider(self, user_message: str) -> str:
    # Your implementation here
    pass
```

Then update the `call_ai()` method to support your provider.

### Custom Ports

If you changed Unity's HTTP port, update `ai_config.json`:
```json
"unity": {
  "http_port": YOUR_PORT_HERE
}
```

---

## Selling This Package

This AI Bridge is **fully standalone** and works with any Unity project. Users just need:
1. Python (embedded with your package)
2. Their own API key
3. Unity project with the web chat

No IDE required! Works in Cursor, VS Code, Rider, Visual Studio, or standalone.

---

## Support

For issues, questions, or feature requests:
- Check Unity Console for server status
- Check AI Bridge console for error messages
- Verify API key is valid and has credits

Enjoy your AI-powered Unity development! 🚀

"""
AI Chat Bridge for Unity
Standalone AI assistant that works with any provider:
- Anthropic Claude (Sonnet, Opus, Haiku)
- OpenAI (GPT-4, GPT-3.5)
- Google Gemini (Gemini 1.5 Pro)
- DeepSeek (DeepSeek Chat/Coder)
- Ollama (local models)

Watches for Unity chat messages and responds automatically via API calls.
No IDE required - just Python and an API key!
"""

import os
import sys
import time
import json
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Configuration
class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from ai_config.json"""
        config_path = Path(__file__).parent / "ai_config.json"
        
        if not config_path.exists():
            self.create_default_config(config_path)
            print(f"Created default config at: {config_path}")
            print("Please edit ai_config.json with your API key and restart!")
            sys.exit(0)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.provider = config.get('provider', 'anthropic')
        self.anthropic_key = config.get('anthropic', {}).get('api_key', '')
        self.anthropic_model = config.get('anthropic', {}).get('model', 'claude-3-5-sonnet-20241022')
        self.openai_key = config.get('openai', {}).get('api_key', '')
        self.openai_model = config.get('openai', {}).get('model', 'gpt-4')
        self.gemini_key = config.get('gemini', {}).get('api_key', '')
        self.gemini_model = config.get('gemini', {}).get('model', 'gemini-1.5-pro')
        self.deepseek_key = config.get('deepseek', {}).get('api_key', '')
        self.deepseek_model = config.get('deepseek', {}).get('model', 'deepseek-chat')
        self.ollama_endpoint = config.get('ollama', {}).get('endpoint', 'http://localhost:11434')
        self.ollama_model = config.get('ollama', {}).get('model', 'llama2')
        self.unity_http_port = config.get('unity', {}).get('http_port', 9765)
        self.check_interval = config.get('settings', {}).get('check_interval', 2)
        self.max_context_messages = config.get('settings', {}).get('max_context_messages', 10)
    
    def create_default_config(self, path: Path):
        """Create default configuration file"""
        default_config = {
            "provider": "anthropic",
            "anthropic": {
                "api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
                "model": "claude-3-5-sonnet-20241022"
            },
            "openai": {
                "api_key": "YOUR_OPENAI_API_KEY_HERE",
                "model": "gpt-4"
            },
            "gemini": {
                "api_key": "YOUR_GEMINI_API_KEY_HERE",
                "model": "gemini-1.5-pro"
            },
            "deepseek": {
                "api_key": "YOUR_DEEPSEEK_API_KEY_HERE",
                "model": "deepseek-chat"
            },
            "ollama": {
                "endpoint": "http://localhost:11434",
                "model": "llama2"
            },
            "unity": {
                "http_port": 9765
            },
            "settings": {
                "check_interval": 2,
                "max_context_messages": 10
            }
        }

        with open(path, 'w') as f:
            json.dump(default_config, f, indent=2)

# Knowledge Base Integration
class KnowledgeBaseContext:
    """Loads project context from NightBlade Knowledge Base"""
    
    def __init__(self):
        project_root = Path(__file__).parent.parent.parent
        self.db_path = project_root / "KnowledgeBase" / "nightblade.db"
        self.enabled = self.db_path.exists()
        
        if not self.enabled:
            print("Note: Knowledge Base not found. AI won't have project context.")
            print(f"      Run: KnowledgeBase/setup_kb.bat to enable")
    
    def get_project_context(self, query: str = None, limit: int = 3) -> str:
        """Get relevant project context for AI"""
        if not self.enabled:
            return ""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if query:
                # Search for relevant docs
                cursor.execute('''
                    SELECT title, category, content
                    FROM documents
                    WHERE content LIKE ?
                    LIMIT ?
                ''', (f'%{query}%', limit))
            else:
                # Get recent/important docs
                cursor.execute('''
                    SELECT title, category, content
                    FROM documents
                    WHERE category IN ('core-systems', 'troubleshooting')
                    ORDER BY last_updated DESC
                    LIMIT ?
                ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return ""
            
            context = "## Project Knowledge:\n\n"
            for title, category, content in results:
                # Truncate long content
                snippet = content[:500] + "..." if len(content) > 500 else content
                context += f"### {title} ({category})\n{snippet}\n\n"
            
            return context
        
        except Exception as e:
            print(f"Warning: KB query failed: {e}")
            return ""
    
    def save_conversation(self, user_msg: str, ai_response: str):
        """Save conversation to KB for future context"""
        if not self.enabled:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table if needed
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT DEFAULT 'unity_chat'
                )
            ''')
            
            cursor.execute('''
                INSERT INTO ai_conversations (user_message, ai_response)
                VALUES (?, ?)
            ''', (user_msg, ai_response))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            print(f"Warning: Failed to save conversation: {e}")

# AI Provider Interface
class AIProvider:
    def __init__(self, config: Config):
        self.config = config
        self.conversation_history = []
        self.kb = KnowledgeBaseContext()
    
    def call_ai(self, user_message: str) -> str:
        """Call the configured AI provider"""
        if self.config.provider == 'anthropic':
            return self._call_anthropic(user_message)
        elif self.config.provider == 'openai':
            return self._call_openai(user_message)
        elif self.config.provider == 'gemini':
            return self._call_gemini(user_message)
        elif self.config.provider == 'deepseek':
            return self._call_deepseek(user_message)
        elif self.config.provider == 'ollama':
            return self._call_ollama(user_message)
        else:
            return f"Error: Unknown provider '{self.config.provider}'"
    
    def _call_anthropic(self, user_message: str) -> str:
        """Call Anthropic Claude API"""
        try:
            import anthropic
            
            if not self.config.anthropic_key or self.config.anthropic_key == "YOUR_ANTHROPIC_API_KEY_HERE":
                return "Error: Please set your Anthropic API key in ai_config.json"
            
            client = anthropic.Anthropic(api_key=self.config.anthropic_key)
            
            # Get project context from Knowledge Base
            kb_context = self.kb.get_project_context(user_message)
            
            # Build system prompt with KB context
            system_prompt = "You are a helpful AI assistant integrated into Unity. You help developers with their Unity projects, answer questions, and provide coding assistance. Be concise and helpful."
            
            if kb_context:
                system_prompt += f"\n\n{kb_context}"
            
            # Build messages with conversation history
            messages = self.conversation_history + [
                {"role": "user", "content": user_message}
            ]
            
            response = client.messages.create(
                model=self.config.anthropic_model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages[-self.config.max_context_messages:]
            )
            
            assistant_message = response.content[0].text
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Trim history
            if len(self.conversation_history) > self.config.max_context_messages * 2:
                self.conversation_history = self.conversation_history[-self.config.max_context_messages * 2:]
            
            # Save to Knowledge Base
            self.kb.save_conversation(user_message, assistant_message)
            
            return assistant_message
            
        except ImportError:
            return "Error: anthropic package not installed. Run: pip install anthropic"
        except Exception as e:
            return f"Error calling Anthropic API: {str(e)}"
    
    def _call_openai(self, user_message: str) -> str:
        """Call OpenAI GPT API"""
        try:
            import openai
            
            if not self.config.openai_key or self.config.openai_key == "YOUR_OPENAI_API_KEY_HERE":
                return "Error: Please set your OpenAI API key in ai_config.json"
            
            client = openai.OpenAI(api_key=self.config.openai_key)
            
            # Get project context from Knowledge Base
            kb_context = self.kb.get_project_context(user_message)
            
            # Build system prompt with KB context
            system_prompt = "You are a helpful AI assistant integrated into Unity. You help developers with their Unity projects, answer questions, and provide coding assistance. Be concise and helpful."
            
            if kb_context:
                system_prompt += f"\n\n{kb_context}"
            
            # Build messages with context
            messages = [
                {"role": "system", "content": system_prompt}
            ] + self.conversation_history + [
                {"role": "user", "content": user_message}
            ]
            
            response = client.chat.completions.create(
                model=self.config.openai_model,
                messages=messages[-self.config.max_context_messages:],
                max_tokens=1024
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Trim history
            if len(self.conversation_history) > self.config.max_context_messages * 2:
                self.conversation_history = self.conversation_history[-self.config.max_context_messages * 2:]
            
            # Save to Knowledge Base
            self.kb.save_conversation(user_message, assistant_message)
            
            return assistant_message
            
        except ImportError:
            return "Error: openai package not installed. Run: pip install openai"
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"

    def _call_gemini(self, user_message: str) -> str:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai

            if not self.config.gemini_key or self.config.gemini_key == "YOUR_GEMINI_API_KEY_HERE":
                return "Error: Please set your Gemini API key in ai_config.json"

            genai.configure(api_key=self.config.gemini_key)

            # Get project context from Knowledge Base
            kb_context = self.kb.get_project_context(user_message)

            # Build system prompt with KB context
            system_prompt = "You are a helpful AI assistant integrated into Unity. You help developers with their Unity projects, answer questions, and provide coding assistance. Be concise and helpful."

            if kb_context:
                system_prompt += f"\n\n{kb_context}"

            # Create model
            model = genai.GenerativeModel(self.config.gemini_model)

            # Build conversation with history
            chat = model.start_chat(history=[])

            # Add conversation history
            for msg in self.conversation_history[-self.config.max_context_messages:]:
                role = "user" if msg["role"] == "user" else "model"
                chat.history.append({
                    "role": role,
                    "parts": [msg["content"]]
                })

            # Send message with system context prepended to first user message
            full_message = f"{system_prompt}\n\n{user_message}" if not self.conversation_history else user_message
            response = chat.send_message(full_message)

            assistant_message = response.text

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            # Trim history
            if len(self.conversation_history) > self.config.max_context_messages * 2:
                self.conversation_history = self.conversation_history[-self.config.max_context_messages * 2:]

            # Save to Knowledge Base
            self.kb.save_conversation(user_message, assistant_message)

            return assistant_message

        except ImportError:
            return "Error: google-generativeai package not installed. Run: pip install google-generativeai"
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"

    def _call_deepseek(self, user_message: str) -> str:
        """Call DeepSeek API (OpenAI-compatible)"""
        try:
            import openai

            if not self.config.deepseek_key or self.config.deepseek_key == "YOUR_DEEPSEEK_API_KEY_HERE":
                return "Error: Please set your DeepSeek API key in ai_config.json"

            # DeepSeek uses OpenAI-compatible API
            client = openai.OpenAI(
                api_key=self.config.deepseek_key,
                base_url="https://api.deepseek.com/v1"
            )

            # Get project context from Knowledge Base
            kb_context = self.kb.get_project_context(user_message)

            # Build system prompt with KB context
            system_prompt = "You are a helpful AI assistant integrated into Unity. You help developers with their Unity projects, answer questions, and provide coding assistance. Be concise and helpful."

            if kb_context:
                system_prompt += f"\n\n{kb_context}"

            # Build messages with context
            messages = [
                {"role": "system", "content": system_prompt}
            ] + self.conversation_history + [
                {"role": "user", "content": user_message}
            ]

            response = client.chat.completions.create(
                model=self.config.deepseek_model,
                messages=messages[-self.config.max_context_messages:],
                max_tokens=1024
            )

            assistant_message = response.choices[0].message.content

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            # Trim history
            if len(self.conversation_history) > self.config.max_context_messages * 2:
                self.conversation_history = self.conversation_history[-self.config.max_context_messages * 2:]

            # Save to Knowledge Base
            self.kb.save_conversation(user_message, assistant_message)

            return assistant_message

        except ImportError:
            return "Error: openai package not installed. Run: pip install openai"
        except Exception as e:
            return f"Error calling DeepSeek API: {str(e)}"

    def _call_ollama(self, user_message: str) -> str:
        """Call local Ollama API"""
        try:
            # Build messages with context
            messages = self.conversation_history + [
                {"role": "user", "content": user_message}
            ]
            
            response = requests.post(
                f"{self.config.ollama_endpoint}/api/chat",
                json={
                    "model": self.config.ollama_model,
                    "messages": messages[-self.config.max_context_messages:],
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return f"Error: Ollama returned status {response.status_code}"
            
            assistant_message = response.json()['message']['content']
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Trim history
            if len(self.conversation_history) > self.config.max_context_messages * 2:
                self.conversation_history = self.conversation_history[-self.config.max_context_messages * 2:]
            
            return assistant_message
            
        except requests.exceptions.ConnectionError:
            return f"Error: Cannot connect to Ollama at {self.config.ollama_endpoint}. Is it running?"
        except Exception as e:
            return f"Error calling Ollama API: {str(e)}"

# Unity Integration
class UnityBridge:
    def __init__(self, config: Config):
        self.config = config
        self.chat_file = Path(__file__).parent / "chat_messages.json"
        self.processed_messages = set()
    
    def check_for_new_messages(self) -> List[Dict]:
        """Check for new unread messages from Unity"""
        if not self.chat_file.exists():
            return []
        
        try:
            with open(self.chat_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content == "[]":
                    return []
                
                messages = json.loads(content)
                new_messages = []
                
                for msg in messages:
                    if (msg.get('sender') == 'User' and 
                        msg.get('unread') == 'true'):
                        
                        msg_id = f"{msg.get('timestamp')}_{msg.get('message')}"
                        if msg_id not in self.processed_messages:
                            new_messages.append(msg)
                            self.processed_messages.add(msg_id)
                
                return new_messages
        
        except Exception as e:
            print(f"Error reading chat file: {e}")
            return []
    
    def send_response_to_unity(self, message: str) -> bool:
        """Send AI response back to Unity via HTTP"""
        try:
            response = requests.post(
                f"http://localhost:{self.config.unity_http_port}/",
                json={
                    "command": "sendchat",
                    "args": {
                        "message": message
                    }
                },
                timeout=5
            )
            
            return response.status_code == 200
        
        except requests.exceptions.ConnectionError:
            print(f"Warning: Cannot connect to Unity on port {self.config.unity_http_port}")
            return False
        except Exception as e:
            print(f"Error sending to Unity: {e}")
            return False
    
    def mark_messages_read(self):
        """Mark processed messages as read in chat file"""
        try:
            if not self.chat_file.exists():
                return
            
            with open(self.chat_file, 'r', encoding='utf-8') as f:
                messages = json.loads(f.read())
            
            # Mark all as read
            for msg in messages:
                if msg.get('sender') == 'User':
                    msg['unread'] = 'false'
            
            with open(self.chat_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2)
        
        except Exception as e:
            print(f"Error marking messages read: {e}")

# Main Application
def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)

def main():
    """Main application loop"""
    log("=" * 60)
    log("AI Chat Bridge for Unity")
    log("=" * 60)
    
    # Load configuration
    try:
        config = Config()
    except Exception as e:
        log(f"Error loading config: {e}")
        return
    
    log(f"Provider: {config.provider}")
    log(f"Unity HTTP Port: {config.unity_http_port}")
    log(f"Check Interval: {config.check_interval}s")
    
    # Initialize components
    ai_provider = AIProvider(config)
    unity_bridge = UnityBridge(config)
    
    if ai_provider.kb.enabled:
        log(f"Knowledge Base: ENABLED (shared context with Cursor AI!)")
    else:
        log(f"Knowledge Base: DISABLED (run KnowledgeBase/setup_kb.bat)")
    
    log("")
    
    log("Watching for Unity chat messages...")
    log("Press Ctrl+C to stop")
    log("")
    
    try:
        while True:
            # Check for new messages
            new_messages = unity_bridge.check_for_new_messages()
            
            if new_messages:
                log(f"Found {len(new_messages)} new message(s)!")
                
                for msg in new_messages:
                    user_message = msg.get('message', '')
                    log(f"User: {user_message}")
                    
                    # Get AI response
                    log(f"Calling {config.provider} API...")
                    ai_response = ai_provider.call_ai(user_message)
                    log(f"AI: {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}")
                    
                    # Send to Unity
                    success = unity_bridge.send_response_to_unity(ai_response)
                    if success:
                        log("Response sent to Unity!")
                    else:
                        log("Could not send to Unity (is it running?)")
                    
                    log("")
                
                # Mark as read
                unity_bridge.mark_messages_read()
            
            time.sleep(config.check_interval)
    
    except KeyboardInterrupt:
        log("")
        log("AI Chat Bridge stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

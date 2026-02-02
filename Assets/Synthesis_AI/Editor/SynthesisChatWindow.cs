using UnityEngine;
using UnityEditor;
using System.Collections.Generic;
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace Synthesis.Editor
{
    /// <summary>
    /// Chat window for communicating with AI assistant directly from Unity
    /// </summary>
    public class SynthesisChatWindow : EditorWindow
    {
        private Vector2 scrollPosition;
        private string inputMessage = "";
        private static List<ChatMessage> chatHistory = new List<ChatMessage>();
        private bool isWaitingForResponse = false;
        private GUIStyle messageStyle;
        private GUIStyle userMessageStyle;
        private GUIStyle aiMessageStyle;
        private GUIStyle inputStyle;
        
        private static SynthesisChatWindow activeWindow;
        
        private class ChatMessage
        {
            public string sender; // "You" or "AI"
            public string message;
            public string timestamp;
            
            public ChatMessage(string sender, string message)
            {
                this.sender = sender;
                this.message = message;
                this.timestamp = DateTime.Now.ToString("HH:mm:ss");
            }
        }
        
        [MenuItem("Synthesis/Advanced/Open IMGUI Chat Window (Legacy)", false, 200)]
        public static void OpenChatWindow()
        {
            // Show notification about new web chat
            bool proceed = EditorUtility.DisplayDialog(
                "Legacy Chat Window",
                "⚠️ You're opening the legacy IMGUI-based chat window.\n\n" +
                "💡 Consider using the new Web Chat instead:\n" +
                "   • Synthesis → Open Web Chat\n" +
                "   • Modern browser-based UI\n" +
                "   • Better styling and features\n" +
                "   • Full HTML/CSS/JavaScript support\n\n" +
                "Do you want to open the legacy window anyway?",
                "Open Legacy Chat",
                "Cancel");
            
            if (!proceed)
                return;
            
            var window = GetWindow<SynthesisChatWindow>("Synthesis Chat (Legacy)");
            window.minSize = new Vector2(400, 300);
            window.Show();
            activeWindow = window;
        }
        
        /// <summary>
        /// Public API for AI to send messages to the chat window
        /// </summary>
        public static void ReceiveAIMessage(string message)
        {
            chatHistory.Add(new ChatMessage("AI", message));
            
            // Force repaint if window is open
            if (activeWindow != null)
            {
                activeWindow.isWaitingForResponse = false;
                activeWindow.scrollPosition = new Vector2(0, float.MaxValue);
                activeWindow.Repaint();
            }
        }
        
        private void OnEnable()
        {
            // Welcome message
            if (chatHistory.Count == 0)
            {
                chatHistory.Add(new ChatMessage("AI", 
                    "👋 Hello! I'm your AI assistant.\n\n" +
                    "I can help you with:\n" +
                    "• Unity development questions\n" +
                    "• Code explanations\n" +
                    "• Real-time scene manipulation\n" +
                    "• Architecture guidance\n" +
                    "• Bug troubleshooting\n\n" +
                    "Type your message below and press Enter or click Send!"));
            }
        }
        
        private void InitStyles()
        {
            if (messageStyle == null)
            {
                messageStyle = new GUIStyle(EditorStyles.label);
                messageStyle.wordWrap = true;
                messageStyle.padding = new RectOffset(10, 10, 5, 5);
                messageStyle.richText = true;
            }
            
            if (userMessageStyle == null)
            {
                userMessageStyle = new GUIStyle(messageStyle);
                userMessageStyle.normal.background = MakeBackground(new Color(0.3f, 0.5f, 0.8f, 0.3f));
                userMessageStyle.padding = new RectOffset(10, 10, 8, 8);
                userMessageStyle.margin = new RectOffset(20, 5, 2, 2);
            }
            
            if (aiMessageStyle == null)
            {
                aiMessageStyle = new GUIStyle(messageStyle);
                aiMessageStyle.normal.background = MakeBackground(new Color(0.2f, 0.2f, 0.2f, 0.5f));
                aiMessageStyle.padding = new RectOffset(10, 10, 8, 8);
                aiMessageStyle.margin = new RectOffset(5, 20, 2, 2);
            }
            
            if (inputStyle == null)
            {
                inputStyle = new GUIStyle(EditorStyles.textArea);
                inputStyle.wordWrap = true;
                inputStyle.padding = new RectOffset(5, 5, 5, 5);
            }
        }
        
        private Texture2D MakeBackground(Color color)
        {
            var texture = new Texture2D(1, 1);
            texture.SetPixel(0, 0, color);
            texture.Apply();
            return texture;
        }
        
        private void OnGUI()
        {
            InitStyles();
            
            // Header
            EditorGUILayout.BeginVertical();
            
            // Title bar
            EditorGUILayout.BeginHorizontal(EditorStyles.toolbar);
            GUILayout.Label("🤖 Synthesis AI Assistant", EditorStyles.boldLabel);
            GUILayout.FlexibleSpace();
            
            if (GUILayout.Button("Clear Chat", EditorStyles.toolbarButton, GUILayout.Width(80)))
            {
                chatHistory.Clear();
                OnEnable(); // Re-add welcome message
            }
            
            EditorGUILayout.EndHorizontal();
            
            // Connection status
            bool connected = SynLinkEditor.IsConnected();
            var statusColor = connected ? "#00ff00" : "#ff0000";
            var statusText = connected ? "● Connected" : "● Disconnected";
            
            EditorGUILayout.BeginHorizontal(EditorStyles.helpBox);
            GUILayout.Label($"<color={statusColor}><b>{statusText}</b></color>", messageStyle);
            GUILayout.FlexibleSpace();
            if (GUILayout.Button("🔄 Refresh", GUILayout.Width(70)))
            {
                Repaint();
            }
            EditorGUILayout.EndHorizontal();
            
            GUILayout.Space(5);
            
            // Chat history (scrollable)
            scrollPosition = EditorGUILayout.BeginScrollView(scrollPosition, GUILayout.ExpandHeight(true));
            
            foreach (var msg in chatHistory)
            {
                DrawChatMessage(msg);
            }
            
            if (isWaitingForResponse)
            {
                EditorGUILayout.BeginHorizontal(aiMessageStyle);
                GUILayout.Label("⏳ AI is thinking...", EditorStyles.miniLabel);
                EditorGUILayout.EndHorizontal();
            }
            
            EditorGUILayout.EndScrollView();
            
            GUILayout.Space(5);
            
            // Input area
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            
            EditorGUILayout.LabelField("Your Message:", EditorStyles.boldLabel);
            
            // Text input with Enter key support
            GUI.SetNextControlName("MessageInput");
            var newMessage = EditorGUILayout.TextArea(inputMessage, inputStyle, GUILayout.MinHeight(60), GUILayout.MaxHeight(120));
            
            // Handle Enter key (Ctrl+Enter to send, Enter for new line)
            if (Event.current.type == EventType.KeyDown && Event.current.keyCode == KeyCode.Return)
            {
                if (Event.current.control || Event.current.command)
                {
                    Event.current.Use();
                    SendMessage();
                }
            }
            
            inputMessage = newMessage;
            
            EditorGUILayout.BeginHorizontal();
            
            GUILayout.FlexibleSpace();
            
            EditorGUI.BeginDisabledGroup(string.IsNullOrWhiteSpace(inputMessage) || isWaitingForResponse);
            if (GUILayout.Button("Send & Notify AI (Ctrl+Enter)", GUILayout.Height(30), GUILayout.Width(200)))
            {
                SendMessage();
                NotifyAI();
            }
            EditorGUI.EndDisabledGroup();
            
            EditorGUILayout.EndHorizontal();
            
            GUILayout.Space(5);
            
            // Hint
            EditorGUILayout.LabelField("💡 Tip: I can control Unity in real-time while we chat!", EditorStyles.miniLabel);
            
            EditorGUILayout.EndVertical();
            
            EditorGUILayout.EndVertical();
        }
        
        private void DrawChatMessage(ChatMessage msg)
        {
            var style = msg.sender == "You" ? userMessageStyle : aiMessageStyle;
            
            EditorGUILayout.BeginVertical(style);
            
            // Header (sender + timestamp)
            EditorGUILayout.BeginHorizontal();
            var icon = msg.sender == "You" ? "👤" : "🤖";
            GUILayout.Label($"<b>{icon} {msg.sender}</b>", messageStyle);
            GUILayout.FlexibleSpace();
            GUILayout.Label($"<color=#888888>{msg.timestamp}</color>", messageStyle);
            EditorGUILayout.EndHorizontal();
            
            GUILayout.Space(3);
            
            // Message content
            GUILayout.Label(msg.message, messageStyle);
            
            EditorGUILayout.EndVertical();
            
            GUILayout.Space(2);
        }
        
        private async void SendMessage()
        {
            if (string.IsNullOrWhiteSpace(inputMessage) || isWaitingForResponse)
                return;
            
            var message = inputMessage.Trim();
            inputMessage = "";
            
            // Add user message to history
            chatHistory.Add(new ChatMessage("You", message));
            
            // Check connection
            if (!SynLinkEditor.IsConnected())
            {
                chatHistory.Add(new ChatMessage("AI", 
                    "❌ Not connected to SynLink server.\n\n" +
                    "Please make sure:\n" +
                    "1. Unity Editor is running\n" +
                    "2. SynLink HTTP server is active (check Console)\n" +
                    "3. Try: Synthesis → Restart HTTP Server"));
                Repaint();
                return;
            }
            
            isWaitingForResponse = true;
            Repaint();
            
            try
            {
                // Send message to AI (logs to console for AI to see)
                var response = await SendToAI(message);
                
                // If we got a response (shouldn't happen - AI uses MCP), add it
                if (!string.IsNullOrEmpty(response))
                {
                    chatHistory.Add(new ChatMessage("AI", response));
                    isWaitingForResponse = false;
                }
                // Otherwise, AI will respond via MCP command which calls ReceiveAIMessage()
                // Keep waiting for 10 more seconds, then timeout
                else
                {
                    var startTime = DateTime.Now;
                    while (isWaitingForResponse && (DateTime.Now - startTime).TotalSeconds < 10)
                    {
                        await Task.Delay(100);
                        if (!isWaitingForResponse) break;
                    }
                    
                    // Timeout - AI didn't respond
                    if (isWaitingForResponse)
                    {
                        isWaitingForResponse = false;
                        chatHistory.Add(new ChatMessage("AI", 
                            "💭 I see your message!\n\n" +
                            "I'm processing it in my main Cursor window. " +
                            "I'll respond here as soon as I can!\n\n" +
                            "Tip: Make sure Cursor is open and connected to the MCP server."));
                    }
                }
            }
            catch (Exception e)
            {
                chatHistory.Add(new ChatMessage("AI", 
                    $"❌ Error: {e.Message}"));
                isWaitingForResponse = false;
            }
            finally
            {
                scrollPosition = new Vector2(0, float.MaxValue); // Scroll to bottom
                Repaint();
            }
        }
        
        /// <summary>
        /// Receive message from user (called by WebSocket)
        /// </summary>
        public static void ReceiveUserMessage(string message)
        {
            // This is called when user sends via WebSocket
            // Just log it - the message is already in the chat history
            Debug.Log($"[💬 USER via WS] {message}");
        }
        
        private void NotifyAI()
        {
            // Multi-pronged approach to get AI's attention:
            
            // 1. Copy to clipboard for easy pasting in Cursor
            EditorGUIUtility.systemCopyBuffer = $"User sent chat message - check Unity Console for [💬 USER] logs";
            
            // 2. Show OS notification
            #if UNITY_EDITOR_WIN
            try
            {
                // Windows notification
                var startInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = "-Command \"Add-Type -AssemblyName System.Windows.Forms; " +
                               "$notify = New-Object System.Windows.Forms.NotifyIcon; " +
                               "$notify.Icon = [System.Drawing.SystemIcons]::Information; " +
                               "$notify.Visible = $true; " +
                               "$notify.ShowBalloonTip(5000, 'Unity Chat', 'New message from user!', " +
                               "[System.Windows.Forms.ToolTipIcon]::Info); " +
                               "Start-Sleep -Seconds 1; " +
                               "$notify.Dispose()\"",
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                System.Diagnostics.Process.Start(startInfo);
            }
            catch { /* Notification failed, that's OK */ }
            #endif
            
            // 3. Try to focus/flash Cursor window (if possible)
            TryFocusCursor();
            
            // 4. Log with VERY OBVIOUS formatting
            Debug.LogWarning("═══════════════════════════════════════════════════");
            Debug.LogWarning("🔔 AI: USER SENT YOU A CHAT MESSAGE!");
            Debug.LogWarning("Check the [💬 USER] log above ↑");
            Debug.LogWarning("═══════════════════════════════════════════════════");
            
            // 5. Play a sound to get attention
            EditorApplication.Beep();
        }
        
        private void TryFocusCursor()
        {
            try
            {
                #if UNITY_EDITOR_WIN
                // Try to find and flash Cursor window
                var startInfo = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "powershell.exe",
                    Arguments = "-Command \"Add-Type @'\n" +
                               "using System;\n" +
                               "using System.Runtime.InteropServices;\n" +
                               "public class Win32 {\n" +
                               "    [DllImport(\\\"user32.dll\\\")]\n" +
                               "    public static extern bool FlashWindowEx(ref FLASHWINFO pwfi);\n" +
                               "    [StructLayout(LayoutKind.Sequential)]\n" +
                               "    public struct FLASHWINFO {\n" +
                               "        public uint cbSize;\n" +
                               "        public IntPtr hwnd;\n" +
                               "        public uint dwFlags;\n" +
                               "        public uint uCount;\n" +
                               "        public uint dwTimeout;\n" +
                               "    }\n" +
                               "}\n" +
                               "'@ -Name Win32 -Namespace FlashWindow; " +
                               "$cursor = Get-Process -Name 'Cursor' -ErrorAction SilentlyContinue | Select-Object -First 1; " +
                               "if ($cursor) { " +
                               "$flash = New-Object FlashWindow.Win32+FLASHWINFO; " +
                               "$flash.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($flash); " +
                               "$flash.hwnd = $cursor.MainWindowHandle; " +
                               "$flash.dwFlags = 0x0000000F; " +
                               "$flash.uCount = 3; " +
                               "$flash.dwTimeout = 0; " +
                               "[FlashWindow.Win32]::FlashWindowEx([ref]$flash); " +
                               "}\"",
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                System.Diagnostics.Process.Start(startInfo);
                #endif
            }
            catch { /* Window flashing failed, that's OK */ }
        }
        
        private async Task<string> SendToAI(string message)
        {
            // Log to Unity Console
            Debug.Log($"[💬 USER] {message}");
            
            // Send via WebSocket to connected clients (MCP server, external tools, etc.)
            SendViaWebSocket(message);
            
            // Give AI a chance to respond via MCP (short wait)
            await Task.Delay(500);
            
            // The AI will use unity_send_chat MCP command to respond
            // If no response after timeout, that's OK - AI might respond later
            
            // Return null - the AI's response will come via ReceiveAIMessage()
            return null;
        }
        
        private void SendViaWebSocket(string message)
        {
            try
            {
                // Create message in JSON format
                string json = JsonConvert.SerializeObject(new
                {
                    type = "chat",
                    sender = "user",
                    message = message,
                    timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
                });
                
                // Broadcast to all WebSocket clients
                SynLinkWebSocket.BroadcastMessage(json);
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[Chat] WebSocket send failed: {e.Message}");
            }
        }
    }
    
}

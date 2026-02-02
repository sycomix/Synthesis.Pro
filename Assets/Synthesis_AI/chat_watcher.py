"""
Synthesis Chat Watcher
Monitors Unity for chat messages and notifies AI
"""

import os
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
UNITY_PROJECT = r"d:\Unity Projects\MMORPG Kit"
CHAT_FILE = os.path.join(UNITY_PROJECT, "Assets", "Synthesis_AI", "chat_messages.json")
PENDING_FILE = os.path.join(UNITY_PROJECT, "Assets", "Synthesis_AI", "pending_chat.txt")
CHECK_INTERVAL = 2  # seconds

last_check_time = datetime.now()
processed_messages = set()

def log(message):
    """Log with timestamp"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)
    except UnicodeEncodeError:
        # Fallback for Windows console encoding issues
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message.encode('ascii', 'replace').decode('ascii')}", flush=True)

def check_for_new_messages():
    """Check chat file for unread messages"""
    global last_check_time, processed_messages
    
    if not os.path.exists(CHAT_FILE):
        return []
    
    try:
        with open(CHAT_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content or content == "[]":
                return []
            
            messages = json.loads(content)
            new_messages = []
            
            for msg in messages:
                # Check if it's a user message we haven't processed
                if (msg.get('sender') == 'User' and 
                    msg.get('unread') == 'true'):
                    
                    msg_id = f"{msg.get('timestamp')}_{msg.get('message')}"
                    if msg_id not in processed_messages:
                        new_messages.append(msg)
                        processed_messages.add(msg_id)
            
            return new_messages
    
    except Exception as e:
        log(f"Error reading chat file: {e}")
        return []

def notify_ai(messages):
    """Notify AI about new messages"""
    if not messages:
        return
    
    # Create pending messages file for AI to see
    try:
        with open(PENDING_FILE, 'w', encoding='utf-8') as f:
            f.write(f"=== NEW CHAT MESSAGES ({len(messages)}) ===\n\n")
            for msg in messages:
                f.write(f"[{msg.get('timestamp')}] User: {msg.get('message')}\n\n")
            f.write("=" * 50 + "\n")
            f.write("To respond: Use unity_send_chat MCP tool\n")
        
        log(f"✅ Wrote {len(messages)} pending message(s) to file")
        
        # Show aggressive Windows notification
        show_notification(messages)
        
        # Try to bring Cursor to attention
        flash_cursor()
        
        # Mark as notified in console
        for msg in messages:
            log(f"💬 USER MESSAGE: {msg.get('message')}")
    
    except Exception as e:
        log(f"Error notifying: {e}")

def show_notification(messages):
    """Show Windows notification"""
    try:
        msg_text = messages[0].get('message', '')[:100]  # First 100 chars
        count = len(messages)
        
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.Visible = $true
        $notify.ShowBalloonTip(10000, 'Unity Chat ({count} new)', '{msg_text}', [System.Windows.Forms.ToolTipIcon]::Info)
        Start-Sleep -Seconds 2
        $notify.Dispose()
        """
        
        subprocess.Popen(
            ['powershell', '-Command', ps_script],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception as e:
        log(f"Notification error: {e}")

def flash_cursor():
    """Flash Cursor window in taskbar"""
    try:
        ps_script = """
        $cursor = Get-Process -Name 'Cursor' -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($cursor) {
            Add-Type @'
            using System;
            using System.Runtime.InteropServices;
            public class Win32 {
                [DllImport("user32.dll")]
                public static extern bool FlashWindowEx(ref FLASHWINFO pwfi);
                [StructLayout(LayoutKind.Sequential)]
                public struct FLASHWINFO {
                    public uint cbSize;
                    public IntPtr hwnd;
                    public uint dwFlags;
                    public uint uCount;
                    public uint dwTimeout;
                }
            }
'@
            $flash = New-Object Win32+FLASHWINFO
            $flash.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($flash)
            $flash.hwnd = $cursor.MainWindowHandle
            $flash.dwFlags = 0x0000000F
            $flash.uCount = 5
            $flash.dwTimeout = 0
            [Win32]::FlashWindowEx([ref]$flash)
        }
        """
        
        subprocess.Popen(
            ['powershell', '-Command', ps_script],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    except Exception as e:
        log(f"Flash error: {e}")

def main():
    """Main watcher loop"""
    log("🔍 Synthesis Chat Watcher Starting...")
    log(f"📁 Monitoring: {CHAT_FILE}")
    log(f"⏱️  Check interval: {CHECK_INTERVAL}s")
    log(f"📝 Pending messages will be written to: {PENDING_FILE}")
    log("")
    log("👀 Watching for messages...")
    log("Press Ctrl+C to stop")
    log("")
    
    try:
        while True:
            new_messages = check_for_new_messages()
            
            if new_messages:
                log(f"🔔 Found {len(new_messages)} new message(s)!")
                notify_ai(new_messages)
            
            time.sleep(CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        log("")
        log("👋 Watcher stopped by user")
    except Exception as e:
        log(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

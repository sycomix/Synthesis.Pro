"""
Add UniTask Conflict and CEF Binaries troubleshooting to NightBlade Knowledge Base
"""
import sqlite3
import sys
from datetime import datetime

def add_troubleshooting_entries():
    """Add UniTask and CEF troubleshooting entries to knowledge base"""
    
    try:
        # Connect to database
        conn = sqlite3.connect('nightblade_kb.db')
        cursor = conn.cursor()
        
        print("[INFO] Connected to NightBlade Knowledge Base")
        
        # Create main document entry
        doc_content = '''# Web Chat and Package Troubleshooting Guide

Complete troubleshooting guide for NightBlade web chat, UnityWebBrowser, and package conflicts.

## UniTask GUID Conflicts

68 GUID conflict warnings between package and embedded UniTask versions.

## CEF Binaries Missing

UnityWebBrowser engine process not found errors.

## Web Chat Setup

Complete setup and configuration guide for browser-based chat interface.
'''
        
        # Insert or update document
        cursor.execute('''
            INSERT OR REPLACE INTO documents 
            (filename, title, category, full_path, content, last_updated, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'web_chat_troubleshooting.md',
            'Web Chat and Package Troubleshooting',
            'troubleshooting',
            'docs/troubleshooting/web_chat_troubleshooting.md',
            doc_content,
            datetime.now().isoformat(),
            len(doc_content.split())
        ))
        
        doc_id = cursor.lastrowid
        print(f"[SUCCESS] Created document (ID: {doc_id})")
        
        # Entry 1: UniTask GUID Conflicts
        cursor.execute('''
            INSERT INTO troubleshooting 
            (document_id, symptom, cause, solution, severity, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            'GUID conflicts for 68 UniTask files - Packages/com.cysharp.unitask vs Assets/.../Plugins/UniTask',
            '''Two installations of UniTask with identical GUIDs:
1. Package version (Packages/com.cysharp.unitask/) - Required by UnityWebBrowser
2. Embedded version (Assets/.../LiteNetLibManager/Plugins/UniTask/) - Bundled with MMORPG KIT asset''',
            '''Delete the embedded copy, keep the package version:

PowerShell:
Remove-Item -Path "Assets/NightBlade/ThirdParty/LiteNetLibManager/Plugins/UniTask" -Recurse -Force

Why this works:
- LiteNetLibManager references UniTask by GUID (f51ebe6a0ceec4240a699833d6309b23)
- Package version has the SAME GUID
- Unity automatically resolves to package version
- Cannot remove package version (UnityWebBrowser requires it as dependency)

Steps:
1. Delete: Assets/NightBlade/ThirdParty/LiteNetLibManager/Plugins/UniTask/
2. Return to Unity (auto-reimports)
3. Verify no GUID conflicts in console
4. LiteNetLibManager continues working via package UniTask''',
            'high',
            'unitask,guid,conflict,duplicate,package,litenetlibmanager,webbrowser,mmorpgkit'
        ))
        print("[SUCCESS] Added UniTask GUID conflict troubleshooting")
        
        # Entry 2: CEF Binaries Missing
        cursor.execute('''
            INSERT INTO troubleshooting 
            (document_id, symptom, cause, solution, severity, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            '[UWB]: The engine process could not be found! FileNotFoundException',
            '''Package is referenced in manifest.json but binaries (~200MB of .exe/.dll files) didn't download during installation.

Often caused by:
- UniTask GUID conflicts interfering with package downloads
- Network issues during package installation
- Corrupted package cache''',
            '''Solution A - Reimport Package (Recommended):
1. Window → Package Manager
2. Find "UnityWebBrowser"
3. Right-click → Reimport
4. Wait 3-5 minutes (~200MB download)
5. Restart Unity

Solution B - Manual CEF Download:
1. Visit: https://cef-builds.spotifycdn.com/index.html
2. Download: Windows 64-bit / Standard Distribution
3. Extract to: UnityWebBrowser/Engine/Cef/Windows/
4. Restart Unity

Verification:
Check if binaries exist in:
Library/PackageCache/dev.voltstro.unitywebbrowser.engine.cef.win.x64@.../
Should contain multiple .exe and .dll files.

Required Packages in manifest.json:
"dev.voltstro.unitywebbrowser": "2.2.8"
"dev.voltstro.unitywebbrowser.engine.cef": "2.2.8"
"dev.voltstro.unitywebbrowser.engine.cef.win.x64": "2.2.8"

Requires VoltUPR scoped registry in manifest.json''',
            'critical',
            'unitywebbrowser,cef,chromium,browser,engine,webchat,binaries,download,filenotfound'
        ))
        print("[SUCCESS] Added CEF binaries troubleshooting")
        
        # Entry 3: Web Chat Configuration
        cursor.execute('''
            INSERT INTO configurations 
            (document_id, setting_name, setting_type, default_value, description, example, related_to)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            'WebBrowserUIFull Component',
            'ScriptableObject',
            'CEF Engine, TCP Communication, Input System Handler',
            '''Required configuration for web chat browser component.

WebBrowserUIFull must have these ScriptableObjects assigned:
- Engine: Select "CEF Engine" from dropdown
- Communication Layer: Select "TCP Communication Layer"  
- Input Handler: Select "Web Browser Input System Handler"

Resolution: 1920x1080 (configurable)
Framerate: 30fps windowless
Memory: ~200MB for browser process''',
            '''Scene: Assets/Scenes/SynthesisChat.unity
GameObject: WebChatBrowser
Component: WebBrowserUIFull
- engine: {fileID: 11400000, guid: 649ce3cfdf00ca615abcf2bb62227f5c}
- communicationLayer: {fileID: 11400000, guid: 05fef73d64ae908d1b4ec02a676d1ccc}
- inputHandler: {fileID: 11400000, guid: 565be9a8022a65c7288f47df26d5fe7f}''',
            'WebChatBridge'
        ))
        print("[SUCCESS] Added web chat configuration")
        
        # Add quick reference entries
        quick_refs = [
            ('Web Chat', 'Open Web Chat', 'Unity Menu → Synthesis → Open Web Chat', 'Opens browser-based modern chat interface', None, doc_id),
            ('Web Chat', 'Open Legacy Chat', 'Unity Menu → Synthesis → Open Legacy Chat Window', 'Opens IMGUI-based fallback chat (no browser needed)', None, doc_id),
            ('Web Chat', 'Restart MCP Servers', 'Unity Menu → Synthesis → Restart MCP Servers', 'Manually restart HTTP and WebSocket servers if port conflicts persist', None, doc_id),
            ('Troubleshooting', 'Fix UniTask Conflicts', 'Delete Assets/.../Plugins/UniTask folder', 'Remove embedded UniTask to resolve 68 GUID conflicts', 'Remove-Item -Recurse -Force', doc_id),
            ('Troubleshooting', 'Reimport UnityWebBrowser', 'Package Manager → UnityWebBrowser → Right-click → Reimport', 'Download missing CEF binaries', None, doc_id),
        ]
        
        for category, title, command, description, example, related_doc_id in quick_refs:
            cursor.execute('''
                INSERT INTO quick_reference 
                (category, title, command, description, example, related_doc_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (category, title, command, description, example, related_doc_id))
        
        print(f"[SUCCESS] Added {len(quick_refs)} quick reference entries")
        
        # Add tags
        tags = [
            ('unitask', 'package'),
            ('guid-conflict', 'troubleshooting'),
            ('unitywebbrowser', 'package'),
            ('cef', 'browser'),
            ('webchat', 'feature'),
            ('troubleshooting', 'documentation'),
            ('synthesis', 'feature'),
        ]
        
        for tag_name, tag_category in tags:
            cursor.execute('''
                INSERT OR IGNORE INTO tags (name, category, usage_count)
                VALUES (?, ?, 1)
            ''', (tag_name, tag_category))
            
            # Get tag ID and associate with document
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
            tag_id = cursor.fetchone()[0]
            
            cursor.execute('''
                INSERT OR IGNORE INTO document_tags (document_id, tag_id)
                VALUES (?, ?)
            ''', (doc_id, tag_id))
        
        print(f"[SUCCESS] Added {len(tags)} tags")
        
        # Commit changes
        conn.commit()
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM troubleshooting WHERE document_id = ?", (doc_id,))
        ts_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM configurations WHERE document_id = ?", (doc_id,))
        config_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM quick_reference WHERE related_doc_id = ?", (doc_id,))
        qr_count = cursor.fetchone()[0]
        
        print(f"\n[INFO] Knowledge Base Updated:")
        print(f"  - Document ID: {doc_id}")
        print(f"  - Troubleshooting entries: {ts_count}")
        print(f"  - Configuration entries: {config_count}")
        print(f"  - Quick reference entries: {qr_count}")
        print(f"  - Tags: {len(tags)}")
        
        # Close connection
        conn.close()
        
        print("\n[SUCCESS] NightBlade troubleshooting database updated successfully!")
        print("\nQuery examples:")
        print("  python nightblade_kb.py search unitask")
        print("  python nightblade_kb.py search cef")
        print("  python nightblade_kb.py search webchat")
        return 0
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(add_troubleshooting_entries())

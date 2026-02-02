# 🤖 Synthesis Chat Watcher

**Automatic AI notification when you send chat messages from Unity!**

---

## 🎯 What It Does

The Chat Watcher runs in the background and:

1. ✅ **Monitors Unity chat** for your messages
2. 🔔 **Notifies AI automatically** when you send a message
3. ⚡ **Flashes Cursor window** to get attention
4. 📝 **Creates pending_chat.txt** for AI to read
5. 🪟 **Shows Windows notifications**

**No more manually telling AI to check!**

---

## 🚀 How to Use

### **Start the Watcher:**

**Option 1: Double-click** 
- `start_chat_watcher.bat` in this folder
- Keep the window open

**Option 2: From Unity**
- Menu: `Synthesis → Start Chat Watcher` (if we add the menu item)

### **Send Messages:**

1. Open Unity chat: `Synthesis → Open Chat Window`
2. Type your message
3. Click "Send & Notify AI"
4. **Chat Watcher automatically notifies AI!**
5. AI sees the notification and responds

---

## 📋 Requirements

- ✅ Windows (uses Windows notifications)
- ✅ Python (uses embedded Python from KnowledgeBase)
- ✅ Unity running with SynLink active

---

## 🔧 How It Works

```
You type in Unity Chat
        ↓
Click "Send & Notify AI"
        ↓
Message written to chat_messages.json
        ↓
Chat Watcher sees it (checks every 2 seconds)
        ↓
Watcher creates pending_chat.txt
        ↓
Watcher flashes Cursor + shows notification
        ↓
AI sees notification/pending file
        ↓
AI reads your message
        ↓
AI responds via unity_send_chat
        ↓
Response appears in Unity chat!
```

---

## ⚙️ Configuration

Edit `chat_watcher.py` to change:

```python
CHECK_INTERVAL = 2  # How often to check (seconds)
```

---

## 🐛 Troubleshooting

### **Watcher won't start:**
- Make sure you ran `KnowledgeBase\setup_kb.bat` first
- Check that Python exists at: `KnowledgeBase\python\python.exe`

### **No notifications appearing:**
- Check if Windows notifications are enabled
- Look at the watcher console - does it see messages?

### **AI still not responding:**
- Make sure Cursor is open
- Check `pending_chat.txt` - are messages being written?
- AI needs to actually see and read the notifications

---

## 💡 Tips

1. **Keep the watcher running** - Start it once when you open Unity
2. **Check pending_chat.txt** if unsure - Shows what AI should see
3. **Watcher logs everything** - Watch the console for activity
4. **Restart if needed** - Close and reopen the watcher window

---

## 🎯 Future Enhancements

- [ ] Add to Unity menu for one-click start
- [ ] Minimize to system tray
- [ ] Sound alerts
- [ ] Multiple Unity project support
- [ ] Status indicator in Unity

---

**Status:** ✅ Ready to use!

# Developer Log Guide

## What is the Developer Log?

The Developer Log is your **private development tracking system** built into Synthesis AI. It helps you organize features, track TODOs, and maintain a clear roadmap for your project.

Think of it as your personal project management tool that lives right inside your Unity project!

---

## 📍 Location

Your developer log lives in:
```
Assets/Synthesis_AI/.devlog/DEVELOPER_LOG.md
```

This folder is separate from the main codebase, making it easy to:
- Keep private notes without cluttering your project
- Exclude from asset store packages (if needed)
- Optionally add to `.gitignore` for truly private notes

---

## 🎯 What Can You Track?

### Feature Backlog
Track planned features with full details:
- **Status**: Planned, In Development, or Completed
- **Location**: Exact file and line number
- **Description**: What needs to be done
- **Priority**: High, Medium, or Low
- **Notes**: Additional context and implementation ideas

### Technical Debt
Keep a running list of code that needs refactoring or improvement over time.

### Completed Work
Maintain a changelog of what you've accomplished, with dates and details.

---

## 💬 Working with AI Assistants

The Developer Log is **AI-friendly**! Your AI assistant (Cursor, Claude Code, Cline, etc.) can:

### Read and Reference
```
"Check the dev log for planned features"
"What's in the feature backlog?"
"Show me high priority TODOs"
```

### Add New Items
```
"Add 'VR controller support' to the dev log"
"Track this as a TODO in the developer log"
"Update the dev log - mark user authentication as completed"
```

### Plan Implementation
```
"Let's implement the next feature from the dev log"
"Show me what needs to be done for the asset loading feature"
```

Just mention "dev log" or "DEVELOPER_LOG" and your AI will know exactly what you're talking about!

---

## 📝 Entry Format

Here's the template for adding new features:

```markdown
#### Feature Name
- **Status**: Planned | In Development | Completed
- **Location**: Assets/YourFolder/YourFile.cs:123
- **Description**: Clear description of what needs to be done
- **Priority**: High | Medium | Low
- **Notes**: Any additional context or implementation details
```

### Example Entry

```markdown
#### Player Inventory System
- **Status**: Planned
- **Location**: Scripts/Player/PlayerController.cs:45
- **Description**: Add inventory system with grid UI and item management
- **Priority**: High
- **Notes**: Should support stacking, drag-and-drop, and item tooltips. Consider using ScriptableObjects for item definitions.
```

---

## 🔄 Workflow Tips

### 1. Start Your Session
Open the dev log to see what's next:
```
"Show me the dev log"
"What's the highest priority feature?"
```

### 2. Track as You Go
When you find TODOs or think of features:
```
"Add this to the dev log as a medium priority feature"
```

### 3. Mark Progress
When you complete work:
```
"Mark the inventory system as completed in the dev log"
```

### 4. Plan Ahead
Use it for sprint planning:
```
"List all high priority features from the dev log"
"What technical debt should we tackle next?"
```

---

## 🎨 Organizing Your Log

### Categories
The default log includes these sections:
- **AI Integration Features** - AI-powered functionality
- **Editor Tools Features** - Unity Editor enhancements
- **MCP Tools Features** - Model Context Protocol improvements
- **Shader Tools Features** - Shader and material tools
- **UI Integration Features** - UI framework integrations
- **Technical Debt** - Code that needs refactoring

Feel free to add your own categories based on your project needs!

### Priority System
- **High**: Must-have features, blocking issues, critical improvements
- **Medium**: Nice-to-have features, quality improvements
- **Low**: Future ideas, polish items, experimental features

---

## 🚀 Quick Start

### View Your Dev Log
1. Navigate to `Assets/Synthesis_AI/.devlog/DEVELOPER_LOG.md`
2. Open in your favorite markdown editor
3. Or ask your AI: "Show me the developer log"

### Add Your First Entry
```markdown
#### My First Feature
- **Status**: Planned
- **Location**: Scripts/MyScript.cs:10
- **Description**: Add awesome new functionality
- **Priority**: High
- **Notes**: This will make the game 10x better!
```

### Work with Your AI
Tell your AI assistant:
```
"Let's implement the first feature from the dev log"
```

---

## 💡 Pro Tips

### 1. Be Specific
Instead of: "Fix the thing"
Write: "Fix GameObject instantiation memory leak in SpawnManager.cs:145"

### 2. Link to Code
Always include file paths and line numbers - your AI can jump right to them!

### 3. Regular Reviews
Schedule time to review and update your dev log. It helps you stay organized and focused.

### 4. Use with Knowledge Base
The dev log complements the Synthesis Knowledge Base. Use them together:
- **Dev Log**: Your personal TODOs and features
- **Knowledge Base**: Shared commands and workflows

### 5. Team Coordination
If working with a team, the dev log helps everyone stay aligned on what's being built and what's coming next.

---

## 🔐 Privacy

Your developer log is **private by default**:
- Lives in `.devlog` folder (hidden by convention)
- Can be added to `.gitignore` if you want to keep notes truly private
- Not included in asset store packages (if you exclude the folder)

---

## ❓ Common Questions

**Q: Can I have multiple dev logs?**
A: Yes! Create separate markdown files for different aspects of your project:
- `FEATURES.md` - Feature planning
- `BUGS.md` - Bug tracking
- `REFACTORING.md` - Code quality improvements

**Q: Does the AI automatically update the dev log?**
A: Your AI assistant can read and update it when you ask, but it won't modify it automatically without your permission.

**Q: Can I customize the format?**
A: Absolutely! The markdown format is flexible. Customize it however you like.

**Q: Should I commit the dev log to version control?**
A: That's up to you! Many developers do commit it for team visibility, while others keep it private.

---

## 🎉 Get Started!

Open your developer log at `Assets/Synthesis_AI/.devlog/DEVELOPER_LOG.md` and start tracking your features today!

Ask your AI:
```
"Show me what's in the developer log"
"Add [feature name] to the dev log"
"Let's work on the next item from the dev log"
```

Happy developing! 🚀

---

*Part of Synthesis AI - Your AI Creative Partner for Unity*

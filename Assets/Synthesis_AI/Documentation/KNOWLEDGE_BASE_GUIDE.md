# Synthesis Knowledge Base Guide

The Synthesis Knowledge Base is a SQLite-powered system that stores all documentation, commands, workflows, examples, and FAQs in a searchable database. This enables AI assistants and developers to quickly find relevant information without manually searching through documentation files.

## 🚀 Quick Start

### Automatic Initialization

When you enable the Knowledge Base in the Synthesis component:
1. A SQLite database is automatically created at `synthesis_knowledge.db` in your project root
2. The database is populated with core Synthesis commands and documentation
3. Search commands become available for querying the knowledge base

### Enable Knowledge Base

1. **Select the Synthesis GameObject** in your scene
2. **In the Inspector**, find the "Knowledge Base" section
3. **Enable Knowledge Base**: ✅ (checked)
4. **Knowledge Base Path**: Leave empty for default location
5. **Press Play** - Database will be created automatically!

---

## 📚 What's Inside the Knowledge Base?

The Knowledge Base contains five main tables:

### 1. **Commands**
All Synthesis commands with:
- Command name and description
- Parameters and their types
- Example requests/responses
- Use cases and related commands
- Common errors and solutions

### 2. **Workflows**
Step-by-step solutions for common tasks:
- Title and description
- Difficulty level (Beginner/Intermediate/Advanced)
- Sequential steps with commands
- Estimated completion time
- Tags for easy searching

### 3. **Examples**
Code snippets and real-world examples:
- Example title and description
- Full JSON command sequences
- Category and difficulty
- Tags for categorization

### 4. **FAQ**
Frequently asked questions:
- Question and detailed answer
- Category (Troubleshooting, UI, etc.)
- Related commands
- Keywords for searching

### 5. **Errors**
Common errors and their solutions:
- Error code and message
- Root cause explanation
- Step-by-step solution
- Related command reference

---

## 🔍 Search Commands

### SearchCommands

Search for Synthesis commands by name, description, or category.

**Parameters:**
- `searchTerm` (string): Text to search for

**Example Request:**
```json
{
  "commands": [{
    "id": "search_1",
    "type": "SearchCommands",
    "parameters": {
      "searchTerm": "GameObject"
    }
  }]
}
```

**Example Response:**
```json
{
  "commandId": "search_1",
  "success": true,
  "message": "Found 3 command(s)",
  "data": {
    "commands": [
      {
        "Id": 1,
        "Name": "FindGameObject",
        "Category": "GameObject Management",
        "Description": "Find a GameObject in the active scene by name",
        "Parameters": "{\"name\":\"string (required)\"}",
        "ExampleRequest": "{\"command\":\"FindGameObject\",\"id\":\"find_obj\",\"parameters\":{\"name\":\"Player\"}}",
        "UseCases": "Locating objects for manipulation, verifying object exists",
        "RelatedCommands": "GetComponent, SetComponentValue"
      }
    ],
    "count": 3
  }
}
```

---

### SearchWorkflows

Search for workflows by tags or title.

**Parameters:**
- `tag` (string): Tag to search for (e.g., "ui", "positioning", "beginner")

**Example Request:**
```json
{
  "commands": [{
    "id": "workflow_1",
    "type": "SearchWorkflows",
    "parameters": {
      "tag": "ui"
    }
  }]
}
```

**Example Response:**
```json
{
  "commandId": "workflow_1",
  "success": true,
  "message": "Found 1 workflow(s)",
  "data": {
    "workflows": [
      {
        "Id": 1,
        "Title": "Move UI Element",
        "Description": "Reposition a UI element to new coordinates",
        "Difficulty": "Beginner",
        "Steps": "[{\"step\":1,\"description\":\"Find the UI element\",\"command\":\"FindGameObject\"}]",
        "CommandsUsed": "FindGameObject, SetComponentValue",
        "EstimatedTime": 2,
        "Tags": "ui, positioning, rectTransform, beginner"
      }
    ],
    "count": 1
  }
}
```

---

### SearchFAQ

Search for answers to common questions.

**Parameters:**
- `searchTerm` (string): Text to search for in questions, answers, or keywords

**Example Request:**
```json
{
  "commands": [{
    "id": "faq_1",
    "type": "SearchFAQ",
    "parameters": {
      "searchTerm": "not responding"
    }
  }]
}
```

**Example Response:**
```json
{
  "commandId": "faq_1",
  "success": true,
  "message": "Found 1 FAQ(s)",
  "data": {
    "faqs": [
      {
        "Id": 1,
        "Question": "Why isn't Synthesis responding to my commands?",
        "Answer": "Check these common issues:\n1. Is Unity in Play mode?...",
        "Category": "Troubleshooting",
        "RelatedCommands": "Ping",
        "Keywords": "not working, not responding, no response"
      }
    ],
    "count": 1
  }
}
```

---

## 💡 Use Cases

### For AI Assistants

AI assistants can search the Knowledge Base to:
- **Learn available commands** before attempting operations
- **Find relevant workflows** for complex tasks
- **Get troubleshooting help** when commands fail
- **Discover examples** for similar problems solved before

**Example AI Workflow:**
```
User: "How do I move a health bar?"
AI: 
  1. SearchWorkflows("ui positioning") → finds "Move UI Element" workflow
  2. SearchCommands("position") → finds SetComponentValue command
  3. Executes FindGameObject("HealthBar")
  4. Executes SetComponentValue with new position
```

### For Developers

Developers can:
- **Query command documentation** programmatically
- **Build custom tools** using the Knowledge Base API
- **Extend the database** with custom commands/workflows
- **Track usage patterns** (future feature)

---

## 🛠️ Advanced Usage

### Custom Database Location

Specify a custom database path in the Inspector:

```
Knowledge Base Path: C:/MyProject/custom_knowledge.db
```

### Accessing the Knowledge Base via Code

**Note:** The Knowledge Base is now an external Python-based system located in the project root `KnowledgeBase/` folder. It's accessed via command-line queries rather than Unity C# API.

```bash
# From KnowledgeBase folder
python\python.exe nightblade_kb.py query "your search term"
```

For AI integration, the Knowledge Base is accessed automatically through the `.cursorrules` file and MCP tools. Unity components don't need direct access.

---

## 📝 Extending the Knowledge Base

### Adding Custom Documentation

You can extend the Knowledge Base by adding your documentation:

1. Add markdown files to `docs/` folder
2. Run the populate script:

```bash
cd KnowledgeBase
python\python.exe populate_kb.py
#endif
```

---

## 🐛 Troubleshooting

### "Knowledge Base is not enabled or initialized"

**Solution:**
1. Check that "Enable Knowledge Base" is checked in Inspector
2. Verify Unity is in Play mode
3. Check Console for initialization errors
4. Ensure file permissions allow database creation

### Database File Not Found

**Solution:**
- The database is created automatically on first run
- Check project root for `synthesis_knowledge.db`
- If missing, delete and enter Play mode again to recreate

### Search Returns No Results

**Solution:**
1. Database might be empty - check if it was populated correctly
2. Try broader search terms (e.g., "find" instead of "FindGameObject")
3. Check spelling of search terms
4. For workflows, try common tags: "ui", "beginner", "positioning"

---

## 🚀 Performance Notes

- **SQLite is fast** - Searches complete in milliseconds
- **Database is small** - Typically under 1MB even with many entries
- **No network required** - Everything runs locally
- **Editor-only** - Knowledge Base is only available in Unity Editor

---

## 🔮 Future Features

Planned enhancements for the Knowledge Base:

- **Usage Analytics** - Track which commands/workflows are used most
- **AI Learning** - Store successful AI problem-solving patterns
- **Community Sharing** - Share workflows and examples with other users
- **Version Control** - Track changes to commands across versions
- **Smart Suggestions** - Recommend related commands based on context

---

## 📚 Related Documentation

- **COMMANDS_REFERENCE.md** - Complete list of all Synthesis commands
- **QUICK_START.md** - Getting started with Synthesis
- **INTEGRATION_GUIDE.md** - Integrating Synthesis with AI tools

---

**The Knowledge Base makes Synthesis smarter with every search! 🧠✨**

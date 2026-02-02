# Synthesis Knowledge Base - Schema Design

**Purpose:** Store all Synthesis knowledge for fast searching and AI learning

---

## 📊 **Database Schema (SQLite or JSON)**

### **Table 1: commands**
*All Synthesis commands with full documentation*

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | INTEGER | Unique ID | 1 |
| name | TEXT | Command name | "FindGameObject" |
| category | TEXT | Command type | "GameObject Management" |
| description | TEXT | What it does | "Finds a GameObject by name" |
| parameters | TEXT (JSON) | Required params | `{"name": "string"}` |
| example_request | TEXT (JSON) | Sample request | Full JSON example |
| example_response | TEXT (JSON) | Sample response | Full JSON example |
| use_cases | TEXT | When to use | "Locating objects for manipulation" |
| related_commands | TEXT | Other commands | "GetComponent, SetComponentValue" |
| version_added | TEXT | Version | "1.0.0" |
| common_errors | TEXT | Typical issues | "GameObject not found" |

### **Table 2: workflows**
*Step-by-step solutions to common tasks*

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | INTEGER | Unique ID | 1 |
| title | TEXT | Workflow name | "Move UI Element" |
| description | TEXT | What it accomplishes | "Repositions UI object in real-time" |
| difficulty | TEXT | Complexity | "Beginner" |
| steps | TEXT (JSON) | Ordered steps | Array of step objects |
| commands_used | TEXT | Command list | "FindGameObject, SetComponentValue" |
| estimated_time | INTEGER | Seconds | 5 |
| tags | TEXT | Search tags | "ui, positioning, transform" |
| times_used | INTEGER | Usage count | 47 |
| success_rate | REAL | Effectiveness | 0.95 |

### **Table 3: examples**
*Code snippets and real-world examples*

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | INTEGER | Unique ID | 1 |
| title | TEXT | Example name | "Batch Update Button Colors" |
| description | TEXT | What it shows | "Changes color of all buttons" |
| code | TEXT | Command sequence | Full JSON commands |
| language | TEXT | Format | "json" |
| category | TEXT | Type | "Batch Operations" |
| tags | TEXT | Search tags | "ui, buttons, colors, batch" |
| difficulty | TEXT | Level | "Intermediate" |
| upvotes | INTEGER | Helpfulness | 23 |

### **Table 4: faq**
*Frequently asked questions*

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | INTEGER | Unique ID | 1 |
| question | TEXT | The question | "Why isn't my command executing?" |
| answer | TEXT | The solution | "Check that Unity is in Play mode..." |
| category | TEXT | Topic | "Troubleshooting" |
| related_commands | TEXT | Commands | "Ping" |
| helpful_count | INTEGER | Votes | 15 |
| keywords | TEXT | Search terms | "not working, not responding" |

### **Table 5: errors**
*Common errors and solutions*

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | INTEGER | Unique ID | 1 |
| error_code | TEXT | Error identifier | "OBJ_NOT_FOUND" |
| error_message | TEXT | Actual message | "GameObject not found" |
| cause | TEXT | Why it happens | "Object doesn't exist in scene" |
| solution | TEXT | How to fix | "Verify object name is correct..." |
| related_command | TEXT | Which command | "FindGameObject" |
| severity | TEXT | Impact level | "Error" |

### **Table 6: ai_interactions** (Future - Learning Layer)
*Track AI problem-solving for collective learning*

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | TEXT | UUID | "abc-123-def" |
| problem_type | TEXT | Category | "ui_positioning" |
| problem_description | TEXT | Anonymized | "Need to move element right" |
| solution_used | TEXT | Workflow ID | "workflow_5" |
| commands_sequence | TEXT (JSON) | Commands used | Array of commands |
| time_to_solve | INTEGER | Seconds | 3 |
| success | BOOLEAN | Worked? | true |
| user_satisfaction | INTEGER | 1-5 rating | 5 |
| created_at | DATETIME | When | "2026-01-28 10:30:00" |
| synced_to_network | BOOLEAN | Uploaded? | false |

---

## 📝 **Sample Data**

### **Sample Command Entry:**
```json
{
  "id": 1,
  "name": "FindGameObject",
  "category": "GameObject Management",
  "description": "Finds a GameObject in the active scene by name",
  "parameters": {
    "name": "string (required) - Name of GameObject to find"
  },
  "example_request": {
    "command": "FindGameObject",
    "id": "find_player",
    "parameters": {
      "name": "Player"
    }
  },
  "example_response": {
    "id": "find_player",
    "success": true,
    "data": {
      "objectId": "12345",
      "name": "Player",
      "position": {"x": 0, "y": 1, "z": 0}
    }
  },
  "use_cases": "Locating objects for manipulation, verifying object exists, getting object references",
  "related_commands": "GetComponent, SetComponentValue, GetChildren",
  "version_added": "1.0.0",
  "common_errors": "GameObject not found - verify name is exact match including case"
}
```

### **Sample Workflow Entry:**
```json
{
  "id": 1,
  "title": "Move UI Element to New Position",
  "description": "Repositions a UI element to specified screen coordinates in real-time",
  "difficulty": "Beginner",
  "steps": [
    {
      "step": 1,
      "description": "Find the UI element",
      "command": "FindGameObject",
      "parameters": {"name": "HealthBar"}
    },
    {
      "step": 2,
      "description": "Update its position",
      "command": "SetComponentValue",
      "parameters": {
        "objectId": "<from step 1>",
        "componentType": "RectTransform",
        "field": "anchoredPosition",
        "value": {"x": 100, "y": 50}
      }
    }
  ],
  "commands_used": "FindGameObject, SetComponentValue",
  "estimated_time": 2,
  "tags": "ui, positioning, rectTransform, beginner",
  "times_used": 0,
  "success_rate": 1.0
}
```

### **Sample FAQ Entry:**
```json
{
  "id": 1,
  "question": "Why isn't Synthesis responding to my commands?",
  "answer": "Check these common issues:\n1. Is Unity in Play mode? Bridge only works during Play.\n2. Is 'Enable Bridge' checked on the Synthesis component?\n3. Are you waiting at least 0.5 seconds between writing command and checking result?\n4. Check synthesis_logs.txt for error messages.\n5. Verify JSON syntax is correct (use a validator).",
  "category": "Troubleshooting",
  "related_commands": "Ping",
  "helpful_count": 0,
  "keywords": "not working, not responding, no response, doesn't work"
}
```

---

## 🔍 **Example Queries**

### **Search for command:**
```sql
SELECT * FROM commands 
WHERE name LIKE '%GameObject%' 
   OR description LIKE '%find object%';
```

### **Get workflow by tags:**
```sql
SELECT * FROM workflows 
WHERE tags LIKE '%ui%' 
  AND difficulty = 'Beginner';
```

### **Find solution to error:**
```sql
SELECT * FROM errors 
WHERE error_message LIKE '%not found%';
```

### **Popular examples:**
```sql
SELECT * FROM examples 
ORDER BY upvotes DESC 
LIMIT 10;
```

---

## 📦 **Storage Format Options**

### **Option A: SQLite (Pros/Cons visible)**
**Pros:**
- Fast queries
- Relational data
- Standard SQL

**Cons:**
- Native library required
- Platform issues (WebGL, IL2CPP)
- Harder to inspect data

### **Option B: JSON Files (One per table)**
```
KnowledgeBase/
├── commands.json       (array of all commands)
├── workflows.json      (array of all workflows)
├── examples.json       (array of all examples)
├── faq.json           (array of all FAQs)
└── errors.json        (array of all errors)
```

**Pros:**
- Human readable
- Easy to edit
- No dependencies
- Version control friendly

**Cons:**
- Slower search
- Need to load all data
- Manual indexing

### **Option C: Hybrid (JSON + Search Index)**
```
KnowledgeBase/
├── data/
│   ├── commands.json
│   ├── workflows.json
│   └── ...
└── search_index.json  (pre-built search index)
```

---

## 🎯 **What I Need You To Review**

1. **Schema Design** - Are these the right tables/fields?
2. **Data Structure** - Is this the information we need?
3. **Storage Format** - SQLite vs JSON vs Hybrid?
4. **Search Strategy** - How should users find information?
5. **Future Sync** - Does this support centralized learning later?

---

## 💡 **Questions for You**

1. Should we include **performance tips** in commands?
2. Should **workflows** track user customizations?
3. Should **examples** allow user contributions (later)?
4. Do we need a **version** field on everything for updates?
5. Should we track **analytics** (what's searched/used most)?

---

**Please review and tell me:**
- ✅ What looks good
- ❌ What to change
- 💡 What's missing
- 🎯 Which storage format to use

Then I can build exactly what you need!


# Synthesis AI - Developer Log
*Private development tracking for features, improvements, and technical debt*

---

## 📋 Feature Backlog

### AI Integration Features

#### ElevenLabs Sound Generation
- **Status**: Planned
- **Priority**: Medium
- **Effort**: Medium
- **Tags**: #ai-integration #audio #api
- **Location**: `Runtime/SynLinkExtended.cs:291`
- **Description**: Integrate ElevenLabs API for AI-powered sound generation
- **Notes**: Requires API key configuration similar to OpenAI integration

#### Trellis 3D Model Generation
- **Status**: Planned
- **Priority**: Medium
- **Effort**: Large
- **Tags**: #ai-integration #3d-models #api #asset-generation
- **Location**: `Runtime/SynLinkExtended.cs:301`
- **Description**: Integrate Trellis API for AI-powered 3D model generation
- **Notes**: Would enable AI-driven asset creation workflow

#### Chat Archive & Session Memory System
- **Status**: Planned
- **Priority**: Medium
- **Effort**: Medium
- **Tags**: #ai-integration #rag #knowledge-base #privacy #learning
- **Location**: `KnowledgeBase/`
- **Description**: Archive AI chat sessions to knowledge base with references in developer log for persistent learning and context
- **Implementation**:
  - Store full conversation transcripts in knowledge_base.db (PRIVATE)
  - Link sessions in developer log with session IDs
  - Enable AI to study user patterns and preferences
  - Searchable by date, topic, tags, and code changes
- **Privacy**: All data stays local, never published
- **Benefit**: AI learns user's coding style, preferences, and workflow for improved collaboration over time
- **Notes**: Creates personalized AI training without external data sharing

### Editor Tools Features

#### VFX Asset Creation Authentication
- **Status**: In Development
- **Priority**: High
- **Effort**: Medium
- **Tags**: #editor-tools #vfx #unity-api #research
- **Location**: `MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:216`
- **Description**: Find authenticated way to create VFX assets programmatically
- **Notes**: Current implementation is incomplete, needs Unity API research

#### Enhanced Hierarchy Path Search
- **Status**: Planned
- **Priority**: Medium
- **Effort**: Quick
- **Tags**: #editor-tools #hierarchy #search #improvement
- **Location**: `Editor/UIChangeApplicator.cs:160`
- **Description**: Implement proper hierarchy path search instead of simple name matching
- **Notes**: Current implementation only searches by object name

#### Script Validation Improvements
- **Status**: Planned
- **Priority**: Medium
- **Effort**: Medium
- **Tags**: #mcp-tools #script-management #validation #code-quality
- **Location**: `MCPForUnity/Editor/Tools/ManageScript.cs:2366`
- **Description**: Improve Unity script validation checks - current approach is naive
- **Notes**: Need better compilation error detection and type checking

#### Script Update Workflow
- **Status**: Planned
- **Priority**: Low
- **Effort**: Quick
- **Tags**: #mcp-tools #script-management #refactoring #technical-debt
- **Location**: `MCPForUnity/Editor/Tools/ManageScript.cs:2503`
- **Description**: Easier way for users to update incorrect scripts
- **Notes**: Currently duplicated with updateScript method, needs refactoring

### MCP Tools Features

#### Console Timestamp Filtering
- **Status**: Planned
- **Priority**: Low
- **Effort**: Quick
- **Tags**: #mcp-tools #console #filtering #feature
- **Location**: `MCPForUnity/Editor/Tools/ReadConsole.cs:175,334,366`
- **Description**: Implement timestamp filtering for console log queries
- **Notes**: Requires adding timestamp data to console entries

#### Expanded Asset Type Support
- **Status**: Planned
- **Priority**: Medium
- **Effort**: Medium
- **Tags**: #mcp-tools #assets #feature-expansion
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:243`
- **Description**: Add support for more asset types (Animation Controller, Scene, etc.)
- **Notes**: Current implementation covers basic types

#### Asset Importer Property Application
- **Status**: Planned
- **Priority**: Low
- **Effort**: Quick
- **Tags**: #mcp-tools #assets #import #feature
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:141`
- **Description**: Apply importer properties before reimporting assets

#### Asset Modification for Additional Types
- **Status**: Planned
- **Priority**: Medium
- **Effort**: Medium
- **Tags**: #mcp-tools #assets #import #feature-expansion
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:450`
- **Description**: Add modification logic for Models, AudioClips, and other importers

#### Enhanced Asset Metadata
- **Status**: Planned
- **Priority**: Low
- **Effort**: Medium
- **Tags**: #mcp-tools #assets #metadata #enhancement
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:1116`
- **Description**: Add more metadata, importer settings, and dependency tracking

#### Component Detail Expansion
- **Status**: Planned
- **Priority**: Low
- **Effort**: Quick
- **Tags**: #mcp-tools #assets #components #enhancement
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:806`
- **Description**: Add more component-specific details to asset queries

### Shader Tools Features

#### Large File Threshold
- **Status**: Planned
- **Priority**: Low
- **Effort**: Quick
- **Tags**: #shader-tools #performance #feature
- **Location**: `MCPForUnity/Editor/Tools/ManageShader.cs:201`
- **Description**: Consider adding threshold for large shader files

#### HLSL Template
- **Status**: Planned
- **Priority**: Low
- **Effort**: Quick
- **Tags**: #shader-tools #templates #feature
- **Location**: `MCPForUnity/Editor/Tools/ManageShader.cs:288`
- **Description**: Create HLSL shader template similar to existing templates

### UI Integration Features

#### Additional UI Integrations
- **Status**: Planned
- **Priority**: Low
- **Effort**: Medium
- **Tags**: #ui-integration #feature-expansion
- **Location**: `Editor/UIIntegrator.cs:301`
- **Description**: Add more UI framework integrations as needed

### External Dependencies

#### Tommy TOML Parser Optimization
- **Status**: Planned
- **Priority**: Low
- **Effort**: Quick
- **Tags**: #performance #optimization #external-deps
- **Location**: `MCPForUnity/Editor/External/Tommy.cs:1549`
- **Description**: Reuse ProcessQuotedValueCharacter method for optimization
- **Notes**: Performance optimization for TOML parsing

---

## 🔧 Technical Debt

*Items to refactor or improve over time*

### Code Quality
- Script update workflow duplication needs refactoring
- Unity validation checks need improvement for better accuracy

---

## ✅ Recently Completed

### 2025-02-02 - Session 3
- **Removed Old In-Editor Chat System**: Deleted 18 files from legacy chat infrastructure
  - Removed SynthesisChatWindow.cs and SynthesisChatWatcher.cs
  - Removed chat_watcher.py, ai_chat_bridge.py, and related batch files
  - Removed web UI components (ClaudeChat, SynthesisChat folders)
  - Removed documentation (CHAT_SOLUTION.md, CHAT_WATCHER_README.md, etc.)
  - Cleaned up code references in SynLinkEditor.cs, SynLinkWebSocket.cs, SynthesisEditorTools.cs
- **Decision**: Focus on Chat Archive & Session Memory System for external AI tool integration instead of in-editor chat

### 2025-02-02 - Session 2
- **Fixed AnthropicAPIClient Warning**: Added `new` keyword to SendMessage to properly hide inherited method
- **Removed Unused Event**: Deleted OnStreamChunk event that was never used
- **Suppressed Deprecated API Warnings**: Added pragma directives for InstanceIDToObject and activeInstanceID to maintain compatibility
- **Fixed FindObjectsOfType Deprecations**: Updated to FindObjectsByType with proper parameters across MCPForUnity
- **Excluded Scipy Test Data**: Renamed test data folders to data~ so Unity ignores them completely

### 2025-02-02 - Session 1
- **Fixed Newtonsoft.Json Integration**: Added package and updated all assembly definitions
- **Fixed Python Path**: Corrected SynthesisChatWatcher to use Assets/Synthesis_AI path
- **Eliminated Deprecation Warnings**: Updated to FindFirstObjectByType and FindObjectsByType
- **Disabled Duplicate DLL Warnings**: Configured Python package DLLs to not load as Unity plugins
- **Updated Setup Instructions**: Fixed path references in error messages

---

## 🧠 Decision Log

*Key technical decisions and their rationale*

### 2025-02-02 - Folder Rename to Synthesis.Pro
- **Decision**: Renamed `Assets/Synthesis_AI` to `Assets/Synthesis.Pro` for brand consistency
- **Rationale**: Matches repository name and project branding
- **Impact**: Updated all file paths in scripts and documentation
- **Tags**: #branding #refactoring

### 2025-02-02 - Deprecated API Handling Strategy
- **Decision**: Use pragma directives to suppress CS0618 warnings instead of migrating to EntityId API
- **Rationale**: EntityId API (`EntityIdToObject`, `activeEntityId`) not available in current Unity version
- **Impact**: Maintains compatibility while keeping Asset Store submission clean
- **Alternative Considered**: EntityId migration (failed - API doesn't exist)
- **Tags**: #unity-api #compatibility #asset-store

### 2025-02-02 - Python Process Cleanup Enhancement
- **Decision**: Added failsafe `KillOrphanedPythonProcesses()` to handle orphaned Python processes on Unity shutdown
- **Rationale**: Python processes (chat watcher, detective mode) were not shutting down reliably, causing folder locking issues
- **Implementation**:
  - Use `Process.Kill(true)` to kill entire process tree
  - Scan for embedded Python processes on shutdown
  - Increased wait timeout from 2s to 3s
- **Tags**: #python #process-management #cleanup

### 2025-02-02 - Developer Log System
- **Decision**: Created structured markdown-based developer log in `.devlog/` folder
- **Rationale**: Provides persistent context for AI assistant across sessions and project tracking for human developers
- **Impact**: Improved AI context retention and human-AI collaboration efficiency
- **Tags**: #documentation #rag #project-management

---

## 📝 Notes

This log tracks planned features, improvements, and technical decisions for Synthesis Pro.

**Format for new feature entries:**
```
#### Feature Name
- **Status**: Planned | In Development | Completed
- **Priority**: Critical | High | Medium | Low
- **Effort**: Quick | Medium | Large
- **Tags**: #category #type #related-system
- **Location**: File path and line number
- **Description**: What needs to be done
- **Notes**: Additional context
```

**Format for decision log entries:**
```
### YYYY-MM-DD - Decision Title
- **Decision**: What was decided
- **Rationale**: Why this approach was chosen
- **Impact**: What changed as a result
- **Alternative Considered**: (optional) Other options evaluated
- **Tags**: #relevant-tags
```

**Common Tags:**
- Systems: #ai-integration #editor-tools #mcp-tools #shader-tools #ui-integration
- Types: #feature #bug-fix #refactoring #optimization #documentation
- Priority: #critical #technical-debt #enhancement

---

*Last Updated: 2025-02-02*


## 📝 Recently Completed Work

### 2026-02-03 - Session 4ddc0859: Chat Archive Setup

**Files Modified:**
- `.cursorrules` (created)
- `RAG/chat_archiver.py` (created)

**Decisions Made:**
- Implement Chat Archive System
  - Rationale: Crown that ties it all together

**Session ID:** `4ddc0859-91b4-48cb-abf2-3fec5475ce4c` (searchable in private KB)

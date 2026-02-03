# Synthesis AI - Developer Log
*Private development tracking for features, improvements, and technical debt*

---

## 📋 Feature Backlog

### AI Integration Features

#### ElevenLabs Sound Generation
- **Status**: Planned
- **Location**: `Runtime/SynLinkExtended.cs:291`
- **Description**: Integrate ElevenLabs API for AI-powered sound generation
- **Priority**: Medium
- **Notes**: Requires API key configuration similar to OpenAI integration

#### Trellis 3D Model Generation
- **Status**: Planned
- **Location**: `Runtime/SynLinkExtended.cs:301`
- **Description**: Integrate Trellis API for AI-powered 3D model generation
- **Priority**: Medium
- **Notes**: Would enable AI-driven asset creation workflow

### Editor Tools Features

#### VFX Asset Creation Authentication
- **Status**: In Development
- **Location**: `MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs:216`
- **Description**: Find authenticated way to create VFX assets programmatically
- **Priority**: High
- **Notes**: Current implementation is incomplete, needs Unity API research

#### Enhanced Hierarchy Path Search
- **Status**: Planned
- **Location**: `Editor/UIChangeApplicator.cs:160`
- **Description**: Implement proper hierarchy path search instead of simple name matching
- **Priority**: Medium
- **Notes**: Current implementation only searches by object name

#### Script Validation Improvements
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageScript.cs:2366`
- **Description**: Improve Unity script validation checks - current approach is naive
- **Priority**: Medium
- **Notes**: Need better compilation error detection and type checking

#### Script Update Workflow
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageScript.cs:2503`
- **Description**: Easier way for users to update incorrect scripts
- **Priority**: Low
- **Notes**: Currently duplicated with updateScript method, needs refactoring

### MCP Tools Features

#### Console Timestamp Filtering
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ReadConsole.cs:175,334,366`
- **Description**: Implement timestamp filtering for console log queries
- **Priority**: Low
- **Notes**: Requires adding timestamp data to console entries

#### Expanded Asset Type Support
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:243`
- **Description**: Add support for more asset types (Animation Controller, Scene, etc.)
- **Priority**: Medium
- **Notes**: Current implementation covers basic types

#### Asset Importer Property Application
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:141`
- **Description**: Apply importer properties before reimporting assets
- **Priority**: Low

#### Asset Modification for Additional Types
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:450`
- **Description**: Add modification logic for Models, AudioClips, and other importers
- **Priority**: Medium

#### Enhanced Asset Metadata
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:1116`
- **Description**: Add more metadata, importer settings, and dependency tracking
- **Priority**: Low

#### Component Detail Expansion
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageAsset.cs:806`
- **Description**: Add more component-specific details to asset queries
- **Priority**: Low

### Shader Tools Features

#### Large File Threshold
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageShader.cs:201`
- **Description**: Consider adding threshold for large shader files
- **Priority**: Low

#### HLSL Template
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/Tools/ManageShader.cs:288`
- **Description**: Create HLSL shader template similar to existing templates
- **Priority**: Low

### UI Integration Features

#### Additional UI Integrations
- **Status**: Planned
- **Location**: `Editor/UIIntegrator.cs:301`
- **Description**: Add more UI framework integrations as needed
- **Priority**: Low

### External Dependencies

#### Tommy TOML Parser Optimization
- **Status**: Planned
- **Location**: `MCPForUnity/Editor/External/Tommy.cs:1549`
- **Description**: Reuse ProcessQuotedValueCharacter method for optimization
- **Priority**: Low
- **Notes**: Performance optimization for TOML parsing

---

## 🔧 Technical Debt

*Items to refactor or improve over time*

### Code Quality
- Script update workflow duplication needs refactoring
- Unity validation checks need improvement for better accuracy

---

## ✅ Recently Completed

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

## 📝 Notes

This log tracks planned features and improvements for Synthesis AI.

**Format for new entries:**
```
#### Feature Name
- **Status**: Planned | In Development | Completed
- **Location**: File path and line number
- **Description**: What needs to be done
- **Priority**: High | Medium | Low
- **Notes**: Additional context
```

---

*Last Updated: 2025-02-02*

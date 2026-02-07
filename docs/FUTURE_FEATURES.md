# Future Features & Improvements

This document tracks potential features and improvements identified during development. These are organized by priority and component.

## High Priority

### Core Features

**ElevenLabs Sound Generation** ([SynLinkExtended.cs:293](../Assets/Synthesis.Pro/Runtime/SynLinkExtended.cs#L293))
- Integrate ElevenLabs API for AI sound generation
- Would enable voice synthesis and audio content generation
- Requires API key and integration work

**Trellis 3D Model Generation** ([SynLinkExtended.cs:303](../Assets/Synthesis.Pro/Runtime/SynLinkExtended.cs#L303))
- Integrate Trellis for 3D model generation from prompts
- Would enable procedural 3D asset creation
- Requires API integration and Unity mesh import

**VFX Asset Creation** ([ManageVFX.cs:216](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/Vfx/ManageVFX.cs#L216))
- Find authenticated way to create VFX Graph assets programmatically
- Currently in development
- Requires Unity API research

### AI Integration

**Phase 3 AI Model Context** ([websocket_server.py:425](../Assets/Synthesis.Pro/Server/websocket_server.py#L425))
- Call AI model with RAG context for enhanced responses
- Would enable full conversational AI with memory
- Depends on Phase 2 RAG completion (now done!)

**Collective Learning** ([rag_bridge.py:121](../Assets/Synthesis.Pro/Server/rag_bridge.py#L121))
- Implement collective learning contribution when enabled
- Would allow sharing insights across sessions (opt-in)
- Requires privacy controls and user consent

## Medium Priority

### UI/UX Improvements

**Search Result Callbacks** ([SynthesisProWindow.cs:731](../Assets/Synthesis.Pro/Editor/SynthesisProWindow.cs#L731))
- Subscribe to result callbacks to populate searchResults
- Would improve search UX with live updates

**Backup List Callbacks** ([SynthesisProWindow.cs:810](../Assets/Synthesis.Pro/Editor/SynthesisProWindow.cs#L810))
- Subscribe to result callbacks to populate backupsList
- Would improve backup management UX

### Asset Management

**Extended Asset Types** ([ManageAsset.cs:243](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageAsset.cs#L243))
- Add support for Animation Controllers, Scenes, etc.
- Would enable more comprehensive asset automation

**Asset Modification for Common Types** ([ManageAsset.cs:450](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageAsset.cs#L450))
- Add modification logic for Models, AudioClips importers
- Would enable programmatic asset tweaking

**Asset Metadata Enhancement** ([ManageAsset.cs:1116](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageAsset.cs#L1116))
- Add more metadata, importer settings, dependencies
- Would improve asset search and organization

**Importer Properties** ([ManageAsset.cs:141](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageAsset.cs#L141))
- Apply importer properties before reimporting
- Would streamline asset pipeline

### Code Analysis

**Improved Unity Checks** ([ManageScript.cs:2366](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageScript.cs#L2366))
- Current Unity script checks are naive and need improvement
- Would provide better code quality analysis

**Script Update Workflow** ([ManageScript.cs:2503](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageScript.cs#L2503))
- Easier way for users to update incorrect scripts
- Currently duplicated with updateScript method
- Requires server-side updates

## Low Priority

### Console & Logging

**Timestamp Filtering** ([ReadConsole.cs:175, 334, 366](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ReadConsole.cs))
- Implement timestamp filtering for console logs
- Requires timestamp data structure
- Would improve log search and debugging

**Component Details** ([ManageAsset.cs:806](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageAsset.cs#L806))
- Add more component-specific details
- Low priority enhancement for inspector data

### Shader Management

**Large File Threshold** ([ManageShader.cs:201](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageShader.cs#L201))
- Consider threshold for large shader files
- Would prevent performance issues

**HLSL Template** ([ManageShader.cs:288](../Assets/Synthesis.Pro/MCPForUnity/Editor/Tools/ManageShader.cs#L288))
- Create HLSL template in addition to GLSL
- Would support more shader types

### Plugin Extensions

**Additional Integrations** ([UIIntegrator.cs:301](../Assets/Synthesis.Pro/Editor/UIIntegrator.cs#L301))
- Add more UI integrations as needed
- Placeholder for future plugins

## Technical Debt

### Third-Party Code

**Tommy TOML Parser** ([Tommy.cs:1549](../Assets/Synthesis.Pro/MCPForUnity/Editor/External/Tommy.cs#L1549))
- Reuse ProcessQuotedValueCharacter method
- Code cleanup in external dependency

---

## Notes

- This list is not prioritized by development order, but by potential impact
- Some features may require external APIs or Unity version updates
- All features should maintain the project philosophy: "Enable, don't force"
- Privacy and user control are paramount for any data-sharing features

## Contributing

When adding new TODOs to code:
1. Add a clear comment explaining what needs to be done
2. Add the item to this document with file reference
3. Assign a priority level based on user impact
4. Consider dependencies and prerequisites

---

**Last Updated:** 2026-02-06

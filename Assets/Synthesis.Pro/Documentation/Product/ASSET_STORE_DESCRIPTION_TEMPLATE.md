# Synthesis.Pro - Asset Store Description Template

**Use this template when creating/updating the Asset Store listing**

---

## ⚠️ THIRD-PARTY API REQUIREMENTS (Must appear at top of description)

**IMPORTANT: Third-Party API Usage & Costs**

Synthesis.Pro integrates with the Anthropic Claude API for AI-powered assistance. To use this package, you will need:

✅ **Anthropic API Account** (https://www.anthropic.com/)
✅ **API Key** (obtained from Anthropic Console: https://console.anthropic.com/)
✅ **Pay-as-you-go API usage** (billed directly by Anthropic, not through Unity Asset Store)

**Approximate API Costs (as of February 2026):**
- Claude Sonnet 4.5: $3.00 per million input tokens, $15.00 per million output tokens
- Typical AI session (10 interactions): $0.02 - $0.10
- Monthly usage (daily developer): ~$3 - $15/month depending on project size and usage patterns

**Cost Savings with Synthesis.Pro:**
This package reduces AI costs by ~85% through intelligent context caching and knowledge base storage. Instead of re-reading your entire project every session, Synthesis.Pro queries stored knowledge - dramatically reducing token usage.

For current Anthropic API pricing, visit: https://www.anthropic.com/pricing

**Terms of Service:** By using this package, you agree to Anthropic's Terms of Service and API Usage Policy.

---

## Product Description

**AI Collaboration for Unity Development with Privacy-First Architecture**

Synthesis.Pro brings professional AI assistance directly into your Unity Editor workflow - helping you code faster, solve problems quicker, and learn as you build.

### Key Features

🤖 **Partnership Model**
- AI that learns your coding style and builds a relationship over time
- Persistent memory across sessions for continuous collaboration
- Context-aware suggestions based on your project history

🔐 **Dual Database Privacy Architecture**
- **Public Database**: Unity documentation, best practices, shared community solutions (shareable)
- **Private Database**: Your project code, AI notes, session history (never shared, stays local)
- Safety First: All data defaults to private to prevent accidental leaks

🔍 **Intelligent Chat with Full Project Context**
- Ask questions about your code with full awareness of your project structure
- Get solutions tailored to your specific implementation
- Privacy-aware: AI knows what's shareable and what stays confidential

🔎 **Hybrid Search System**
- Semantic search: Find concepts, not just keywords
- Keyword search: Traditional exact matching
- Searches across both public Unity knowledge and your private project data

💾 **Database Management**
- Backup your AI relationship and project knowledge
- Restore from previous sessions
- Clear and reset when starting new projects
- Export public knowledge to share with team (private data never included)

💰 **Cost Efficient**
- Save ~85% on AI API costs through smart context management
- One-time project indexing vs. re-reading files every session
- Typical savings: $5-10/month for daily users
- See EFFICIENT_WORKFLOW.md for detailed cost analysis

### What's Included

- **C# Scripts**: Full Unity Editor integration with SynLink bridge system
- **Python Runtime**: Embedded Python 3.11 for RAG (Retrieval-Augmented Generation) system
- **Node.js Server**: WebSocket server for Unity-AI communication
- **Knowledge Base**: SQLite with vector similarity search
- **Documentation**: Comprehensive guides for installation, usage, and integration
- **First-Time Setup**: Automated dependency initialization and database setup
- **Update Checker**: Automatic notification of new versions

### Technical Requirements

- **Unity Version**: 2021.3 or newer
- **Platform**: Windows (Mac and Linux support planned)
- **Anthropic API**: Requires active API key (see cost information above)
- **Disk Space**: ~2GB for Python dependencies and knowledge base
- **Internet**: Required for AI API calls and first-time setup

### Philosophy

> "Privacy isn't about having something to hide - it's about having space to think, learn, and collaborate freely."

Both you and your AI partner deserve privacy for honest collaboration. Synthesis.Pro ensures your project code, experimental ideas, and learning journey stay confidential while still benefiting from community knowledge.

### Use Cases

**For Solo Developers:**
- Debug complex issues with AI that knows your entire codebase
- Learn Unity best practices contextually as you work
- Get unstuck without context-switching to documentation

**For Teams:**
- Share public knowledge base across team members
- Onboard new developers with AI that understands your project
- Document decisions and patterns automatically

**For Learners:**
- AI tutor that adapts to your skill level
- Explanations in context of YOUR code
- Build confidence through iterative learning

### Getting Started

1. Import Synthesis.Pro package
2. Tools → Synthesis → Setup → First Time Setup (one-click dependency installation)
3. Configure Anthropic API key in Unity Preferences
4. Tools → Synthesis → Add SynLink to Scene
5. Start collaborating with AI!

See included documentation for detailed setup instructions and workflow examples.

### Support & Updates

- **GitHub**: https://github.com/Fallen-Entertainment/Synthesis.Pro
- **Documentation**: Included in package (README.md, INSTALLATION.md, etc.)
- **Update Notifications**: Automatic in-editor update checker
- **Issue Tracking**: GitHub Issues for bug reports and feature requests

### Third-Party Notices

This package includes open-source software components. See "Third-Party Notices.txt" in the package for complete license information and attributions.

Included dependencies:
- Newtonsoft.Json (MIT License)
- SQLite (Public Domain)
- Python 3.11 (PSF License)
- Node.js (MIT License)
- NumPy, SciPy, PyTorch, sentence-transformers, and other Python packages (BSD/Apache/MIT licenses)

All licenses are compatible with commercial use and do not require your projects to be open-sourced.

### Privacy & Data Policy

**What Synthesis.Pro collects:**
- Nothing. All data stays on your local machine.

**What Anthropic API receives:**
- Project code and questions you send to the AI (as per their API Terms)
- See Anthropic's Privacy Policy: https://www.anthropic.com/legal/privacy

**What stays private:**
- Everything in synthesis_private.db (your project, AI notes, session history)
- Never transmitted, never shared, never leaves your machine

**What can be shared (optional):**
- Public knowledge in synthesis_knowledge.db (Unity docs, best practices)
- Only if you explicitly use the "Sync Public Knowledge" feature

---

## Asset Tags / Keywords

AI, Artificial Intelligence, Claude, Anthropic, Code Assistant, RAG, Knowledge Base, Developer Tools, Productivity, Code Generation, Documentation, Learning, Tutorial, Education, Workflow, Automation, Editor Extension, Unity Editor, Development, Programming Assistant, Machine Learning, Natural Language Processing, Context-Aware, Privacy, Local-First, Database

---

## Category

**Tools / Add-Ons**

---

## Version History

See CHANGELOG.md for detailed version history.

**Current Version: 1.1.0-beta**

---

## Legal / Compliance Notes

1. This package includes executables (Python and Node.js runtimes) as native dependencies required for core functionality
2. These dependencies provide the AI/ML infrastructure for RAG (Retrieval-Augmented Generation)
3. Similar to packages that include native plugins for video processing, physics, etc.
4. All executables are from trusted, official sources (python.org, nodejs.org)
5. No malicious code, no external connections except user-initiated API calls
6. Full transparency: all code is readable and modifiable by users

**Justification for Executable Dependencies:**

Synthesis.Pro requires Python and Node.js to function because:
- **Python**: Runs the RAG system (vector embeddings, similarity search, knowledge base queries)
- **Node.js**: Provides WebSocket server for Unity-AI communication bridge
- **User Experience**: One-click setup vs. requiring users to manually install and configure environments
- **Target Audience**: Users seeking AI help often lack technical expertise for manual dependency management
- **Precedent**: Similar to how video processing packages include FFmpeg, 3D packages include native renderers, etc.

The embedded runtimes ensure "download and use immediately" functionality that is essential for this product's value proposition.

---

**Built with ❤️ for the Unity community**

🤝 Available on Unity Asset Store - Empowering developers through AI collaboration

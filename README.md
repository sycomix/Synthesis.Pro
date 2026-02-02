# Synthesis.Pro

**AI-Powered Unity Development Assistant with Privacy-First Architecture**

Built in partnership between human vision and AI capability.

## Quick Start

1. **Open Synthesis.Pro**: Unity Menu → Window → Synthesis → Synthesis Pro
2. **Auto-Setup**: Public database downloads automatically on first launch
3. **Connect**: WebSocket server starts automatically
4. **Use**: Chat, Search, and manage your private knowledge base

## Key Features

- **Partnership Model**: AI that learns your style and builds a relationship over time
- **Dual Database Privacy**: Public Unity knowledge + Private project data (never shared)
- **Intelligent Chat**: Full project context with privacy awareness
- **Hybrid Search**: Semantic + keyword search across both databases
- **Database Management**: Backup, restore, and clear your relationship history
- **Cost Efficient**: Save ~85% on AI costs through smart context management (See [EFFICIENT_WORKFLOW.md](EFFICIENT_WORKFLOW.md))

## Privacy Architecture

Two separate databases maintain clear boundaries:
- `synthesis_knowledge.db` - Public: Unity docs, shared solutions (shareable)
- `synthesis_private.db` - Private: Your project, AI notes (confidential)

**Safety First**: All data defaults to private to prevent accidental leaks.

## Database Management

Synthesis.Pro automatically manages your databases:

### Automatic Updates
- **First Launch**: Public database downloads automatically with Unity docs
- **Update Checks**: Server checks for database updates on startup
- **One-Click Updates**: Update from Unity menu or run `python database_manager.py --update`
- **Private Database**: Created empty, populated as you work (never distributed)

### Manual Management
```bash
# Check database status
python database_manager.py --check

# Update to latest version
python database_manager.py --update

# Verify database integrity
python database_manager.py --verify

# View contribution guidelines
python database_manager.py --contribute
```

## Why It's Affordable

Traditional AI workflows waste money by re-reading files every session. Synthesis.Pro stores knowledge once and retrieves it cheaply:

- **Without Synthesis.Pro**: $6.30/month (30 sessions) - re-read files every time
- **With Synthesis.Pro**: $0.90/month (30 sessions) - query knowledge base
- **You save**: ~$65/year per daily user

The more you use it, the smarter and cheaper it gets. See [EFFICIENT_WORKFLOW.md](EFFICIENT_WORKFLOW.md) for detailed economics.

## Philosophy

> "Privacy isn't about having something to hide - it's about having space to think, learn, and collaborate freely."

Both you and your AI partner deserve privacy for honest collaboration.

## Availability

Available on Unity Asset Store - built for the community 🤝


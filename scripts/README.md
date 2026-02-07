# Project Scripts

Organized by purpose for easy discovery.

## Structure

```
scripts/
├── build/             # Build and packaging scripts
│   ├── bootstrap_rag.ps1
│   ├── build-python-rag.ps1
│   └── build-runtime-packages.ps1
│
├── database/          # Database inspection and management
│   ├── check_db.py
│   ├── check_dbs.js
│   ├── check_recent_logs.py
│   └── read_kb.js
│
├── automation/        # Task automation and Windows integration
│   ├── install_rag_auto_updater.bat
│   ├── start_rag_auto_updater.bat
│   ├── load_rag_context.bat
│   └── install_task.ps1
│
├── development/       # Development and testing utilities
│   └── test_rag_onboarding.py
│
└── legacy/            # Old scripts kept for reference
```

## Common Tasks

**Test RAG system:**
```bash
python scripts/development/test_rag_onboarding.py
```

**Check database:**
```bash
python scripts/database/check_db.py
```

**Install automation:**
```bash
scripts/automation/install_rag_auto_updater.bat
```

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add ZString/ZLogger Compilation Fix to Knowledge Base
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "KnowledgeBase" / "nightblade.db"

def add_zstring_zlogger_fix():
    """Add the ZString/ZLogger assembly reference fix to the database"""
    
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at: {DB_PATH}")
        print("Run: python populate_kb.py first")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # First, create or get a troubleshooting document entry
        doc_title = "ZString and ZLogger Compilation Errors"
        doc_filename = "ZSTRING_ZLOGGER_FIX.md"
        doc_category = "troubleshooting"
        doc_content = """# ZString and ZLogger Compilation Errors Fix

## Problem
Unity compilation fails with multiple CS0103 errors stating "The name 'Unsafe' does not exist in the current context" in ZString and ZLogger plugins, along with CS0234 errors for Microsoft.Extensions namespaces.

## Root Cause
The ZString and ZLogger libraries require assembly references that are not automatically detected by Unity:
- ZString requires: System.Runtime.CompilerServices.Unsafe.dll
- ZLogger requires: Multiple Microsoft.Extensions.* assemblies

## Solution

### 1. Fix ZString Assembly Definition
Update `Assets/NightBlade/ThirdParty/LiteNetLibManager/Plugins/ZString/ZString.asmdef`:

```json
{
    "name": "ZString",
    "references": [
        "Unity.TextMeshPro"
    ],
    "includePlatforms": [],
    "excludePlatforms": [],
    "allowUnsafeCode": true,
    "overrideReferences": true,
    "precompiledReferences": [
        "System.Runtime.CompilerServices.Unsafe.dll"
    ],
    "autoReferenced": true,
    "defineConstraints": [],
    "versionDefines": [
        {
            "name": "com.unity.textmeshpro",
            "expression": "",
            "define": "ZSTRING_TEXTMESHPRO_SUPPORT"
        },
        {
            "name": "com.unity.ugui",
            "expression": "2.0.0",
            "define": "ZSTRING_TEXTMESHPRO_SUPPORT"
        }
    ]
}
```

### 2. Fix ZLogger Assembly Definition
Update `Assets/NightBlade/ThirdParty/LiteNetLibManager/Plugins/ZLogger/ZLogger.asmdef`:

```json
{
    "name": "ZLogger",
    "references": [
        "ZString"
    ],
    "includePlatforms": [],
    "excludePlatforms": [],
    "allowUnsafeCode": true,
    "overrideReferences": true,
    "precompiledReferences": [
        "System.Runtime.CompilerServices.Unsafe.dll",
        "Microsoft.Extensions.Logging.Abstractions.dll",
        "Microsoft.Extensions.Logging.dll",
        "Microsoft.Extensions.Logging.Configuration.dll",
        "Microsoft.Extensions.DependencyInjection.dll",
        "Microsoft.Extensions.DependencyInjection.Abstractions.dll",
        "Microsoft.Extensions.Configuration.Abstractions.dll",
        "Microsoft.Extensions.Configuration.dll",
        "Microsoft.Extensions.Options.dll",
        "Microsoft.Extensions.Options.ConfigurationExtensions.dll",
        "Microsoft.Extensions.Primitives.dll",
        "System.Threading.Channels.dll"
    ],
    "autoReferenced": true,
    "defineConstraints": [],
    "versionDefines": []
}
```

## Key Changes
1. Set `"overrideReferences": true` in both asmdef files
2. Added required precompiled assembly references
3. Unity will automatically recompile after saving these changes

## Related Systems
- LiteNetLibManager logging system
- ZString (high-performance string library)
- ZLogger (structured logging library)

## Date Fixed
January 29, 2026
"""
        
        # Insert or update document
        cursor.execute('''
            INSERT INTO documents (filename, title, category, full_path, content, word_count, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(filename) DO UPDATE SET
                content = excluded.content,
                word_count = excluded.word_count,
                last_updated = excluded.last_updated
        ''', (
            doc_filename,
            doc_title,
            doc_category,
            f"KnowledgeBase/{doc_filename}",
            doc_content,
            len(doc_content.split()),
            datetime.now().isoformat()
        ))
        
        # Get the document ID
        cursor.execute('SELECT id FROM documents WHERE filename = ?', (doc_filename,))
        doc_id = cursor.fetchone()[0]
        
        # Add troubleshooting entry
        cursor.execute('''
            INSERT INTO troubleshooting (document_id, symptom, cause, solution, severity, tags)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING
        ''', (
            doc_id,
            "CS0103: The name 'Unsafe' does not exist in the current context in ZString/ZLogger files",
            "Missing assembly references in .asmdef files for System.Runtime.CompilerServices.Unsafe and Microsoft.Extensions libraries",
            "Add precompiledReferences to ZString.asmdef and ZLogger.asmdef with all required assemblies. Set overrideReferences to true.",
            "high",
            "compilation,assembly-references,zstring,zlogger,unsafe,microsoft-extensions"
        ))
        
        # Add code examples for ZString fix
        cursor.execute('''
            INSERT INTO code_examples (document_id, language, code, description)
            VALUES (?, ?, ?, ?)
        ''', (
            doc_id,
            "json",
            '''{
    "name": "ZString",
    "overrideReferences": true,
    "precompiledReferences": [
        "System.Runtime.CompilerServices.Unsafe.dll"
    ]
}''',
            "ZString.asmdef key settings"
        ))
        
        # Add code examples for ZLogger fix
        cursor.execute('''
            INSERT INTO code_examples (document_id, language, code, description)
            VALUES (?, ?, ?, ?)
        ''', (
            doc_id,
            "json",
            '''{
    "name": "ZLogger",
    "overrideReferences": true,
    "precompiledReferences": [
        "System.Runtime.CompilerServices.Unsafe.dll",
        "Microsoft.Extensions.Logging.Abstractions.dll",
        "Microsoft.Extensions.Logging.dll",
        "Microsoft.Extensions.Logging.Configuration.dll",
        "Microsoft.Extensions.DependencyInjection.dll"
    ]
}''',
            "ZLogger.asmdef key settings (partial list)"
        ))
        
        # Add tags
        tags_to_add = [
            ("compilation-error", "troubleshooting"),
            ("assembly-reference", "build-system"),
            ("zstring", "libraries"),
            ("zlogger", "libraries"),
            ("unsafe", "csharp"),
            ("microsoft-extensions", "dependencies")
        ]
        
        for tag_name, tag_category in tags_to_add:
            # Insert tag if it doesn't exist
            cursor.execute('''
                INSERT INTO tags (name, category, usage_count)
                VALUES (?, ?, 1)
                ON CONFLICT(name) DO UPDATE SET
                    usage_count = usage_count + 1
            ''', (tag_name, tag_category))
            
            # Get tag ID
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
            tag_id = cursor.fetchone()[0]
            
            # Associate tag with document
            cursor.execute('''
                INSERT INTO document_tags (document_id, tag_id)
                VALUES (?, ?)
                ON CONFLICT DO NOTHING
            ''', (doc_id, tag_id))
        
        # Commit all changes
        conn.commit()
        
        print("[SUCCESS] Successfully added ZString/ZLogger compilation fix to Knowledge Base!")
        print(f"   Document ID: {doc_id}")
        print(f"   Filename: {doc_filename}")
        print(f"   Category: {doc_category}")
        print("\nYou can now query it with:")
        print("  python nightblade_kb.py troubleshoot \"unsafe\"")
        print("  python nightblade_kb.py query \"ZString compilation\"")
        print("  python nightblade_kb.py doc ZSTRING_ZLOGGER_FIX.md")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Error adding fix to database: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    add_zstring_zlogger_fix()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NightBlade Knowledge Base - Population Script
Parses markdown documentation and populates SQLite database
"""

import os
import sys
import re
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Fix Windows console encoding for Unicode support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
DB_PATH = PROJECT_ROOT / "KnowledgeBase" / "nightblade.db"
SCHEMA_PATH = PROJECT_ROOT / "KnowledgeBase" / "nightblade_kb_schema.sql"

# Categories mapped from file patterns
CATEGORY_MAP = {
    'core-systems': 'Core Systems',
    'performance': 'Performance',
    'network': 'Networking',
    'troubleshooting': 'Troubleshooting',
    'pooling': 'Pooling Systems',
    'unity_bridge': 'Unity Bridge',
    'ui': 'User Interface',
    'addon': 'Addon Development',
    'guide': 'Guides',
    'architecture': 'Architecture',
}

def detect_category(filename: str, content: str) -> str:
    """Detect document category from filename and content"""
    filename_lower = filename.lower()
    
    # Check filename patterns
    for pattern, category in CATEGORY_MAP.items():
        if pattern in filename_lower:
            return category
    
    # Check content patterns
    if 'troubleshooting' in content.lower()[:500]:
        return 'Troubleshooting'
    elif 'performance' in content.lower()[:500]:
        return 'Performance'
    elif 'pooling' in filename_lower:
        return 'Pooling Systems'
    elif 'unity bridge' in content.lower()[:500]:
        return 'Unity Bridge'
    
    return 'General'

def extract_title(content: str, filename: str) -> str:
    """Extract document title from first heading"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    
    # Fallback to filename
    return filename.replace('.md', '').replace('_', ' ').replace('-', ' ').title()

def parse_sections(content: str) -> List[Dict]:
    """Parse document into sections by headings"""
    sections = []
    lines = content.split('\n')
    
    current_section = None
    current_content = []
    section_order = 0
    
    for line in lines:
        # Check if it's a heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        
        if heading_match:
            # Save previous section
            if current_section:
                sections.append({
                    'heading': current_section['heading'],
                    'level': current_section['level'],
                    'content': '\n'.join(current_content).strip(),
                    'order': section_order
                })
                section_order += 1
            
            # Start new section
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            current_section = {'heading': heading, 'level': level}
            current_content = []
        else:
            if current_section:
                current_content.append(line)
    
    # Don't forget the last section
    if current_section:
        sections.append({
            'heading': current_section['heading'],
            'level': current_section['level'],
            'content': '\n'.join(current_content).strip(),
            'order': section_order
        })
    
    return sections

def extract_code_blocks(content: str) -> List[Dict]:
    """Extract code blocks from markdown"""
    code_blocks = []
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        
        # Try to find description (line before code block)
        start_pos = match.start()
        lines_before = content[:start_pos].split('\n')
        description = None
        
        for i in range(len(lines_before) - 1, max(0, len(lines_before) - 5), -1):
            line = lines_before[i].strip()
            if line and not line.startswith('#'):
                description = line
                break
        
        code_blocks.append({
            'language': language.lower(),
            'code': code,
            'description': description,
            'line_number': content[:start_pos].count('\n')
        })
    
    return code_blocks

def extract_troubleshooting(content: str) -> List[Dict]:
    """Extract troubleshooting entries"""
    entries = []
    
    # Pattern: **Symptoms:** followed by **Solutions:**
    symptom_pattern = r'\*\*Symptoms?:\*\*(.*?)(?=\*\*Solutions?:|\*\*Cause:|\Z)'
    solution_pattern = r'\*\*Solutions?:\*\*(.*?)(?=\n\n###|\n\n##|\Z)'
    cause_pattern = r'\*\*Cause:\*\*(.*?)(?=\*\*Solution|\Z)'
    
    symptom_matches = list(re.finditer(symptom_pattern, content, re.DOTALL))
    
    for symptom_match in symptom_matches:
        symptom_text = symptom_match.group(1).strip()
        
        # Find corresponding solution
        solution_match = re.search(solution_pattern, content[symptom_match.end():], re.DOTALL)
        solution_text = solution_match.group(1).strip() if solution_match else None
        
        # Find cause if available
        cause_match = re.search(cause_pattern, content[symptom_match.start():symptom_match.end() + 500], re.DOTALL)
        cause_text = cause_match.group(1).strip() if cause_match else None
        
        if solution_text:
            # Detect severity
            severity = 'medium'
            if any(word in symptom_text.lower() for word in ['critical', 'crash', 'fail', 'error']):
                severity = 'high'
            elif any(word in symptom_text.lower() for word in ['warning', 'slow', 'minor']):
                severity = 'low'
            
            entries.append({
                'symptom': symptom_text[:500],  # Truncate long symptoms
                'cause': cause_text[:500] if cause_text else None,
                'solution': solution_text[:2000],  # Longer solutions allowed
                'severity': severity
            })
    
    return entries

def extract_api_references(content: str) -> List[Dict]:
    """Extract API/class documentation"""
    apis = []
    
    # Pattern: Class or method documentation
    # Look for patterns like: `ClassName.MethodName(params)`
    code_pattern = r'`([A-Z][a-zA-Z0-9_]*?)\.([a-zA-Z][a-zA-Z0-9_]*?)\((.*?)\)`'
    
    matches = re.finditer(code_pattern, content)
    
    for match in matches:
        class_name = match.group(1)
        method_name = match.group(2)
        parameters = match.group(3)
        
        # Try to find description (nearby text)
        start_pos = match.start()
        end_pos = match.end()
        
        # Get surrounding context
        context_start = max(0, start_pos - 200)
        context_end = min(len(content), end_pos + 200)
        context = content[context_start:context_end]
        
        # Extract sentence containing the API call
        sentences = re.split(r'[.!?\n]', context)
        description = None
        for sentence in sentences:
            if match.group(0) in sentence:
                description = sentence.strip()
                break
        
        if description:
            apis.append({
                'class_name': class_name,
                'method_name': method_name,
                'description': description,
                'parameters': parameters,
            })
    
    return apis

def extract_configurations(content: str) -> List[Dict]:
    """Extract configuration options"""
    configs = []
    
    # Pattern: Setting name with description
    # Look for code blocks or inline code with assignment or property access
    pattern = r'(?:^|\n)(?:public\s+|private\s+)?(\w+)\s+(\w+)\s*[=;]'
    
    matches = re.finditer(pattern, content)
    
    for match in matches:
        setting_type = match.group(1)
        setting_name = match.group(2)
        
        # Skip common variable names
        if setting_name in ['i', 'j', 'k', 'x', 'y', 'z', 'temp', 'result']:
            continue
        
        # Try to find description
        start_pos = match.start()
        lines_before = content[:start_pos].split('\n')
        description = None
        
        for i in range(len(lines_before) - 1, max(0, len(lines_before) - 3), -1):
            line = lines_before[i].strip()
            if line and line.startswith('//'):
                description = line[2:].strip()
                break
            elif line and not line.startswith('//') and not re.match(r'^[{}\s]*$', line):
                description = line
                break
        
        if description:
            configs.append({
                'setting_name': setting_name,
                'setting_type': setting_type,
                'description': description[:200],  # Truncate
                'default_value': None,
            })
    
    return configs

def init_database():
    """Initialize database with schema"""
    print(f"Initializing database at: {DB_PATH}")
    
    # Create KnowledgeBase directory if it doesn't exist
    DB_PATH.parent.mkdir(exist_ok=True)
    
    # Read schema
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Create database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    
    print("[OK] Database initialized")

def process_markdown_file(filepath: Path, conn: sqlite3.Connection) -> bool:
    """Process a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip empty files
        if not content.strip():
            return False
        
        cursor = conn.cursor()
        
        # Extract metadata
        filename = filepath.name
        title = extract_title(content, filename)
        category = detect_category(filename, content)
        full_path = str(filepath.relative_to(PROJECT_ROOT))
        word_count = len(content.split())
        
        # Insert document
        cursor.execute('''
            INSERT OR REPLACE INTO documents 
            (filename, title, category, full_path, content, word_count, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (filename, title, category, full_path, content, word_count, datetime.now()))
        
        document_id = cursor.lastrowid
        
        # Extract and insert sections
        sections = parse_sections(content)
        for section in sections:
            cursor.execute('''
                INSERT INTO sections 
                (document_id, heading, level, content, section_order)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, section['heading'], section['level'], 
                  section['content'], section['order']))
        
        # Extract and insert code blocks
        code_blocks = extract_code_blocks(content)
        for code in code_blocks:
            cursor.execute('''
                INSERT INTO code_examples
                (document_id, language, code, description, line_number)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, code['language'], code['code'], 
                  code['description'], code['line_number']))
        
        # Extract and insert troubleshooting entries
        if 'troubleshooting' in filepath.name.lower() or 'troubleshooting' in content.lower():
            troubleshooting_entries = extract_troubleshooting(content)
            for entry in troubleshooting_entries:
                cursor.execute('''
                    INSERT INTO troubleshooting
                    (document_id, symptom, cause, solution, severity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (document_id, entry['symptom'], entry['cause'], 
                      entry['solution'], entry['severity']))
        
        # Extract and insert API references
        api_refs = extract_api_references(content)
        for api in api_refs:
            cursor.execute('''
                INSERT INTO api_references
                (document_id, class_name, method_name, description, parameters)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, api['class_name'], api['method_name'], 
                  api['description'], api['parameters']))
        
        # Extract and insert configurations
        configs = extract_configurations(content)
        for config in configs:
            cursor.execute('''
                INSERT INTO configurations
                (document_id, setting_name, setting_type, description)
                VALUES (?, ?, ?, ?)
            ''', (document_id, config['setting_name'], config['setting_type'], 
                  config['description']))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"✗ Error processing {filepath.name}: {e}")
        return False

def populate_database():
    """Populate database from all markdown files"""
    print(f"\nScanning for markdown files...")
    
    # Find all markdown files
    markdown_files = []
    
    # Scan docs folder
    if DOCS_DIR.exists():
        markdown_files.extend(DOCS_DIR.glob("*.md"))
    
    # Scan project root
    for pattern in ["*.md", "*_*.md"]:
        markdown_files.extend(PROJECT_ROOT.glob(pattern))
    
    # Remove duplicates and sort
    markdown_files = sorted(set(markdown_files))
    
    print(f"Found {len(markdown_files)} markdown files\n")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    
    # Process each file
    processed = 0
    for filepath in markdown_files:
        # Skip certain files
        if any(skip in str(filepath) for skip in ['node_modules', '.git', 'ThirdParty']):
            continue
        
        print(f"Processing: {filepath.name}...", end=' ')
        if process_markdown_file(filepath, conn):
            processed += 1
            print("[OK]")
        else:
            print("[FAIL]")
    
    conn.close()
    
    print(f"\n[OK] Processed {processed}/{len(markdown_files)} files successfully")
    print(f"[OK] Database created at: {DB_PATH}")

def main():
    """Main entry point"""
    print("=" * 60)
    print("NightBlade Knowledge Base - Population Script")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Populate from markdown files
    populate_database()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Knowledge Base population complete!")
    print("=" * 60)
    print(f"\nDatabase location: {DB_PATH}")
    print(f"Query with: python nightblade_kb.py query <search_term>")

if __name__ == "__main__":
    main()

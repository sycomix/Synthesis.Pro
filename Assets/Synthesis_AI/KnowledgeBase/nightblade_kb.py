#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NightBlade Knowledge Base - Query Tool
Fast CLI for searching NightBlade documentation
"""

import os
import sys
import sqlite3
import argparse
from pathlib import Path
from typing import List, Dict

# Fix Windows console encoding for Unicode support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "KnowledgeBase" / "nightblade.db"

class KnowledgeBase:
    """NightBlade Knowledge Base query interface"""
    
    def __init__(self, db_path: Path = DB_PATH):
        if not db_path.exists():
            raise FileNotFoundError(
                f"Knowledge Base not found at: {db_path}\n"
                f"Run: python populate_kb.py"
            )
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Full-text search across all documents"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                d.id, d.filename, d.title, d.category, d.full_path,
                snippet(documents_fts, 2, '<mark>', '</mark>', '...', 30) as snippet
            FROM documents_fts
            JOIN documents d ON documents_fts.rowid = d.id
            WHERE documents_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        ''', (query, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_sections(self, query: str, limit: int = 10) -> List[Dict]:
        """Search within document sections"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                s.id, s.heading, s.level,
                d.filename, d.title, d.category,
                snippet(sections_fts, 1, '<mark>', '</mark>', '...', 30) as snippet
            FROM sections_fts
            JOIN sections s ON sections_fts.rowid = s.id
            JOIN documents d ON s.document_id = d.id
            WHERE sections_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        ''', (query, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_code(self, query: str, language: str = None, limit: int = 10) -> List[Dict]:
        """Search code examples"""
        cursor = self.conn.cursor()
        
        if language:
            cursor.execute('''
                SELECT 
                    c.id, c.language, c.code, c.description,
                    d.filename, d.title
                FROM code_examples c
                JOIN documents d ON c.document_id = d.id
                WHERE c.code LIKE ? AND c.language = ?
                LIMIT ?
            ''', (f'%{query}%', language, limit))
        else:
            cursor.execute('''
                SELECT 
                    c.id, c.language, c.code, c.description,
                    d.filename, d.title
                FROM code_examples c
                JOIN documents d ON c.document_id = d.id
                WHERE c.code LIKE ?
                LIMIT ?
            ''', (f'%{query}%', limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search_troubleshooting(self, query: str, limit: int = 10) -> List[Dict]:
        """Search troubleshooting entries"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                t.id, t.symptom, t.cause, t.solution, t.severity,
                d.filename, d.title
            FROM troubleshooting t
            JOIN documents d ON t.document_id = d.id
            WHERE t.symptom LIKE ? OR t.solution LIKE ?
            ORDER BY 
                CASE t.severity 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_api(self, class_name: str = None, method_name: str = None) -> List[Dict]:
        """Get API/class documentation"""
        cursor = self.conn.cursor()
        
        if class_name and method_name:
            cursor.execute('''
                SELECT 
                    a.*, d.filename, d.title
                FROM api_references a
                JOIN documents d ON a.document_id = d.id
                WHERE a.class_name = ? AND a.method_name = ?
            ''', (class_name, method_name))
        elif class_name:
            cursor.execute('''
                SELECT 
                    a.*, d.filename, d.title
                FROM api_references a
                JOIN documents d ON a.document_id = d.id
                WHERE a.class_name LIKE ?
            ''', (f'%{class_name}%',))
        else:
            return []
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_config(self, setting_name: str) -> List[Dict]:
        """Get configuration option details"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.*, d.filename, d.title
            FROM configurations c
            JOIN documents d ON c.document_id = d.id
            WHERE c.setting_name LIKE ?
        ''', (f'%{setting_name}%',))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def list_categories(self) -> List[str]:
        """List all document categories"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM documents ORDER BY category')
        return [row[0] for row in cursor.fetchall()]
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get all documents in a category"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, title, category, word_count
            FROM documents
            WHERE category = ?
            ORDER BY title
        ''', (category,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_document(self, filename: str) -> Dict:
        """Get full document by filename"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM documents WHERE filename = ?
        ''', (filename,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def stats(self) -> Dict:
        """Get Knowledge Base statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM documents')
        stats['documents'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sections')
        stats['sections'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM code_examples')
        stats['code_examples'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM troubleshooting')
        stats['troubleshooting'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM api_references')
        stats['api_references'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM configurations')
        stats['configurations'] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def print_result(result: Dict, result_type: str = "document"):
    """Pretty print a search result"""
    if result_type == "document":
        print(f"\n[DOC] {result['title']}")
        print(f"      File: {result['filename']}")
        print(f"      Category: {result['category']}")
        if 'snippet' in result:
            snippet = result['snippet'].replace('<mark>', '').replace('</mark>', '')
            print(f"      {snippet}")
    
    elif result_type == "section":
        print(f"\n[SECTION] {result['heading']}")
        print(f"          Document: {result['title']} ({result['filename']})")
        if 'snippet' in result:
            snippet = result['snippet'].replace('<mark>', '').replace('</mark>', '')
            print(f"          {snippet}")
    
    elif result_type == "code":
        print(f"\n[CODE] {result['language']} Example")
        print(f"       Document: {result['title']}")
        if result['description']:
            print(f"       Description: {result['description']}")
        print(f"       {result['code'][:200]}{'...' if len(result['code']) > 200 else ''}")
    
    elif result_type == "troubleshooting":
        severity_label = "[HIGH]" if result['severity'] == 'high' else "[MED]" if result['severity'] == 'medium' else "[LOW]"
        print(f"\n{severity_label} Troubleshooting Entry")
        print(f"        Symptom: {result['symptom'][:100]}")
        if result['cause']:
            print(f"        Cause: {result['cause'][:100]}")
        print(f"        Solution: {result['solution'][:200]}...")
        print(f"        Document: {result['filename']}")
    
    elif result_type == "api":
        print(f"\n[API] {result['class_name']}.{result['method_name']}()")
        if result['parameters']:
            print(f"      Parameters: {result['parameters']}")
        print(f"      {result['description']}")
        if result['example_usage']:
            print(f"      Example: {result['example_usage'][:100]}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='NightBlade Knowledge Base Query Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  nightblade_kb.py query "MapSpawn"
  nightblade_kb.py search-code "CentralNetworkManager" --language csharp
  nightblade_kb.py troubleshoot "connection failed"
  nightblade_kb.py api CentralNetworkManager StartServer
  nightblade_kb.py categories
  nightblade_kb.py stats
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Search all documentation')
    query_parser.add_argument('search_term', help='Search term or phrase')
    query_parser.add_argument('--limit', type=int, default=10, help='Max results (default: 10)')
    
    # Search sections
    sections_parser = subparsers.add_parser('search-sections', help='Search document sections')
    sections_parser.add_argument('search_term', help='Search term or phrase')
    sections_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    # Search code
    code_parser = subparsers.add_parser('search-code', help='Search code examples')
    code_parser.add_argument('search_term', help='Search term or phrase')
    code_parser.add_argument('--language', help='Filter by language (csharp, bash, etc.)')
    code_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    # Troubleshooting
    trouble_parser = subparsers.add_parser('troubleshoot', help='Search troubleshooting solutions')
    trouble_parser.add_argument('search_term', help='Error message or symptom')
    trouble_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    # API lookup
    api_parser = subparsers.add_parser('api', help='Get API documentation')
    api_parser.add_argument('class_name', help='Class name')
    api_parser.add_argument('method_name', nargs='?', help='Method name (optional)')
    
    # Config lookup
    config_parser = subparsers.add_parser('config', help='Get configuration option details')
    config_parser.add_argument('setting_name', help='Configuration setting name')
    
    # Categories
    subparsers.add_parser('categories', help='List all documentation categories')
    
    # Category docs
    cat_docs_parser = subparsers.add_parser('category', help='List documents in category')
    cat_docs_parser.add_argument('category', help='Category name')
    
    # Get document
    doc_parser = subparsers.add_parser('doc', help='Get full document by filename')
    doc_parser.add_argument('filename', help='Document filename')
    
    # Stats
    subparsers.add_parser('stats', help='Show Knowledge Base statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        kb = KnowledgeBase()
        
        if args.command == 'query':
            results = kb.search(args.search_term, args.limit)
            print(f"\n[SEARCH] Found {len(results)} result(s) for '{args.search_term}':")
            for result in results:
                print_result(result, "document")
        
        elif args.command == 'search-sections':
            results = kb.search_sections(args.search_term, args.limit)
            print(f"\n[SEARCH] Found {len(results)} section(s) matching '{args.search_term}':")
            for result in results:
                print_result(result, "section")
        
        elif args.command == 'search-code':
            results = kb.search_code(args.search_term, args.language, args.limit)
            print(f"\n[SEARCH] Found {len(results)} code example(s):")
            for result in results:
                print_result(result, "code")
        
        elif args.command == 'troubleshoot':
            results = kb.search_troubleshooting(args.search_term, args.limit)
            print(f"\n[SEARCH] Found {len(results)} troubleshooting solution(s):")
            for result in results:
                print_result(result, "troubleshooting")
        
        elif args.command == 'api':
            results = kb.get_api(args.class_name, args.method_name if hasattr(args, 'method_name') else None)
            print(f"\n[SEARCH] Found {len(results)} API reference(s):")
            for result in results:
                print_result(result, "api")
        
        elif args.command == 'config':
            results = kb.get_config(args.setting_name)
            print(f"\n[SEARCH] Found {len(results)} configuration(s):")
            for result in results:
                print(f"\n⚙️  {result['setting_name']} ({result['setting_type']})")
                print(f"   {result['description']}")
                print(f"   Document: {result['filename']}")
        
        elif args.command == 'categories':
            categories = kb.list_categories()
            print("\n📂 Documentation Categories:")
            for cat in categories:
                print(f"  • {cat}")
        
        elif args.command == 'category':
            docs = kb.get_by_category(args.category)
            print(f"\n📂 Documents in '{args.category}':")
            for doc in docs:
                print(f"  • {doc['title']} ({doc['filename']}) - {doc['word_count']} words")
        
        elif args.command == 'doc':
            doc = kb.get_document(args.filename)
            if doc:
                print(f"\n📄 {doc['title']}")
                print(f"   File: {doc['filename']}")
                print(f"   Category: {doc['category']}")
                print(f"   Path: {doc['full_path']}")
                print(f"   Words: {doc['word_count']}")
                print(f"\n{doc['content']}")
            else:
                print(f"✗ Document not found: {args.filename}")
        
        elif args.command == 'stats':
            stats = kb.stats()
            print("\n[STATS] Knowledge Base Statistics:")
            print(f"  Documents: {stats['documents']}")
            print(f"  Sections: {stats['sections']}")
            print(f"  Code Examples: {stats['code_examples']}")
            print(f"  Troubleshooting Entries: {stats['troubleshooting']}")
            print(f"  API References: {stats['api_references']}")
            print(f"  Configuration Options: {stats['configurations']}")
        
        kb.close()
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

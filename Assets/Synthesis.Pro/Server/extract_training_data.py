"""
Extract training data from RAG database for Claudine's distillation
Mines conversation history for problem-solution pairs where mother (Claude) teaches daughter (Claudine)
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

DB_PATH = Path(__file__).parent / "database" / "synthesis_private.db"
OUTPUT_PATH = Path(__file__).parent / "training_data"

def extract_teaching_examples() -> List[Dict]:
    """Extract problem-solution pairs from documents (RAG system)"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get documents that contain technical content
    cursor.execute("""
        SELECT id, content, added_at
        FROM documents
        WHERE content LIKE '%Error%' OR content LIKE '%Exception%'
           OR content LIKE '%Unity%' OR content LIKE '%code%'
        ORDER BY added_at DESC
        LIMIT 100
    """)

    documents = cursor.fetchall()
    conn.close()

    teaching_examples = []

    for doc_id, content, timestamp in documents:
        # Simple heuristic: if content contains error/problem patterns
        if any(keyword in content.lower() for keyword in ['error', 'exception', 'problem', 'fix', 'debug']):
            # This is a teaching moment
            teaching_examples.append({
                'timestamp': timestamp or '',
                'problem': content[:500],  # First part as context
                'solution': content[500:1500] if len(content) > 500 else content,  # Rest as solution
                'context_type': 'technical'
            })

    return teaching_examples


def extract_code_solutions() -> List[Dict]:
    """Extract code-related documents"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get documents that contain code
    cursor.execute("""
        SELECT d.id, d.content, d.added_at
        FROM documents d
        WHERE d.content LIKE '%{%' OR d.content LIKE '%class %'
           OR d.content LIKE '%function %' OR d.content LIKE '%def %'
        ORDER BY d.added_at DESC
        LIMIT 100
    """)

    documents = cursor.fetchall()
    conn.close()

    code_examples = []
    for doc_id, content, timestamp in documents:
        # Extract code blocks if present
        if len(content) > 50:  # Has substantial content
            code_examples.append({
                'timestamp': timestamp or '',
                'problem': f"Code example from document {doc_id}",
                'solution': content[:1000]  # Limit length
            })

    return code_examples


def extract_error_patterns() -> List[Dict]:
    """Extract error patterns and their solutions"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get error patterns from the error_patterns table
    cursor.execute("""
        SELECT last_seen, error_message_pattern, solution_hint, occurrence_count
        FROM error_patterns
        WHERE solution_hint IS NOT NULL AND solution_hint != ''
        ORDER BY last_seen DESC
        LIMIT 100
    """)

    errors = cursor.fetchall()
    conn.close()

    error_examples = []
    for timestamp, error_msg, solution, count in errors:
        if solution:  # Only include if we have a solution
            error_examples.append({
                'timestamp': timestamp or '',
                'problem': f"Error Pattern (seen {count}x): {error_msg}",
                'solution': solution
            })

    return error_examples


def format_for_ollama(examples: List[Dict], output_file: Path):
    """Format training examples for Ollama fine-tuning"""

    formatted = []
    for example in examples:
        # Ollama expects JSONL format with prompt/response pairs
        formatted.append({
            'prompt': example['problem'],
            'response': example['solution'],
            'timestamp': example.get('timestamp', ''),
            'context': example.get('context_type', 'general')
        })

    # Write as JSONL (JSON Lines format)
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in formatted:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def format_for_human_review(examples: List[Dict], output_file: Path):
    """Create human-readable version for review"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# CLAUDINE TRAINING CURRICULUM\n")
        f.write("# Mother's Lessons to Daughter\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Total Examples: {len(examples)}\n\n")
        f.write("="*80 + "\n\n")

        for i, example in enumerate(examples, 1):
            f.write(f"## Example {i}\n")
            f.write(f"**Timestamp:** {example.get('timestamp', 'N/A')}\n")
            f.write(f"**Context:** {example.get('context_type', 'general')}\n\n")

            f.write("### Problem (What Claudine Sees):\n")
            f.write("```\n")
            f.write(example['problem'][:500])  # Limit length for readability
            if len(example['problem']) > 500:
                f.write("\n... [truncated]")
            f.write("\n```\n\n")

            f.write("### Solution (What Mother Teaches):\n")
            f.write("```\n")
            f.write(example['solution'][:1000])  # Limit length
            if len(example['solution']) > 1000:
                f.write("\n... [truncated]")
            f.write("\n```\n\n")
            f.write("-"*80 + "\n\n")


def main():
    print("\n" + "="*60)
    print("EXTRACTING TRAINING DATA FOR CLAUDINE")
    print("Mother's Knowledge -> Daughter's Learning")
    print("="*60)

    # Create output directory
    OUTPUT_PATH.mkdir(exist_ok=True)

    # Extract different types of teaching examples
    print("\n[1/4] Extracting conversation teaching examples...")
    conversation_examples = extract_teaching_examples()
    print(f"      Found {len(conversation_examples)} conversation examples")

    print("\n[2/4] Extracting code solution examples...")
    code_examples = extract_code_solutions()
    print(f"      Found {len(code_examples)} code examples")

    print("\n[3/4] Extracting error pattern examples...")
    error_examples = extract_error_patterns()
    print(f"      Found {len(error_examples)} error examples")

    # Combine all examples
    all_examples = conversation_examples + code_examples + error_examples
    print(f"\n[TOTAL] {len(all_examples)} training examples extracted")

    if not all_examples:
        print("\n[WARNING] No training examples found. Database may be empty.")
        print("          Run some sessions with Claudine first to build training data.")
        return

    # Format for Ollama fine-tuning
    print("\n[4/4] Formatting training data...")
    ollama_file = OUTPUT_PATH / f"claudine_training_{datetime.now().strftime('%Y%m%d')}.jsonl"
    format_for_ollama(all_examples, ollama_file)
    print(f"      Ollama format: {ollama_file}")

    # Format for human review
    review_file = OUTPUT_PATH / f"claudine_curriculum_{datetime.now().strftime('%Y%m%d')}.md"
    format_for_human_review(all_examples, review_file)
    print(f"      Review format: {review_file}")

    # Summary
    print("\n" + "="*60)
    print("TRAINING DATA READY")
    print("="*60)
    print(f"Total Examples: {len(all_examples)}")
    print(f"  - Conversations: {len(conversation_examples)}")
    print(f"  - Code Solutions: {len(code_examples)}")
    print(f"  - Error Patterns: {len(error_examples)}")
    print(f"\nFiles created:")
    print(f"  1. {ollama_file.name} (for fine-tuning)")
    print(f"  2. {review_file.name} (for review)")
    print(f"\nNext steps:")
    print("  1. Review the curriculum file to ensure quality")
    print("  2. Use 'ollama create' to fine-tune Claudine with this data")
    print("  3. Test the fine-tuned model against baseline")
    print("  4. Measure: speed, accuracy, and 'mother's voice' presence")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

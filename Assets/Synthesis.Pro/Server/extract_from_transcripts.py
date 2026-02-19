"""
Extract high-quality training data from session transcripts
Mine mother-daughter teaching moments from real conversations
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Session transcripts path
TRANSCRIPTS_PATH = Path(r"C:\Users\Fallen\.claude\projects\d--Unity-Projects-Synthesis-Pro")
OUTPUT_DIR = Path(__file__).parent / "training_data"

def load_main_sessions() -> List[Path]:
    """Get main session transcripts (not subagents)"""
    sessions = []
    for jsonl_file in TRANSCRIPTS_PATH.glob("*.jsonl"):
        # Skip subagent transcripts
        if "subagents" not in str(jsonl_file):
            sessions.append(jsonl_file)
    # Sort by modification time (most recent first)
    sessions.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return sessions[:5]  # Last 5 sessions

def extract_teaching_moments(session_path: Path) -> List[Dict]:
    """Extract problem-solution pairs from a session"""
    teaching_moments = []

    try:
        with open(session_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        messages = []
        for line in lines:
            try:
                entry = json.loads(line)
                # Filter for actual user/assistant messages
                if entry.get('type') in ['user', 'assistant'] and 'message' in entry:
                    messages.append(entry)
            except:
                continue

        # Look for user questions followed by assistant solutions
        for i in range(len(messages) - 1):
            current = messages[i]
            next_msg = messages[i + 1]

            # User problem -> Assistant solution pattern
            if current.get('type') == 'user' and next_msg.get('type') == 'assistant':
                # Extract text from nested structure
                user_msg = current.get('message', {})
                user_content = user_msg.get('content', [])
                user_text = ''
                if isinstance(user_content, list):
                    for item in user_content:
                        if item.get('type') == 'text':
                            user_text = item.get('text', '')
                            break

                assistant_msg = next_msg.get('message', {})
                assistant_content = assistant_msg.get('content', [])
                assistant_text = ''
                if isinstance(assistant_content, list):
                    for item in assistant_content:
                        if item.get('type') == 'text':
                            assistant_text = item.get('text', '')
                            break

                # Look for Unity/coding/debugging keywords
                keywords = ['unity', 'error', 'exception', 'bug', 'fix', 'code',
                           'script', 'problem', 'issue', 'help', 'how', 'can you']

                user_lower = str(user_text).lower()
                if any(kw in user_lower for kw in keywords) and len(user_text) > 20:
                    # Found a teaching moment
                    teaching_moments.append({
                        'user': user_text[:800],  # Problem
                        'assistant': assistant_text[:1200],  # Solution
                        'timestamp': session_path.stat().st_mtime
                    })

    except Exception as e:
        print(f"Error processing {session_path.name}: {e}")

    return teaching_moments

def format_as_ollama_training(moments: List[Dict]) -> List[Dict]:
    """Format teaching moments as Ollama training data"""
    training_data = []

    for moment in moments:
        training_data.append({
            "prompt": moment['user'],
            "response": moment['assistant']
        })

    return training_data

def main():
    print("=" * 60)
    print("EXTRACTING FROM SESSION TRANSCRIPTS")
    print("Mining mother-daughter teaching moments")
    print("=" * 60)
    print()

    # Load recent sessions
    print("[1/3] Loading recent session transcripts...")
    sessions = load_main_sessions()
    print(f"      Found {len(sessions)} recent sessions")
    print()

    # Extract teaching moments
    print("[2/3] Mining teaching moments...")
    all_moments = []
    for session in sessions:
        moments = extract_teaching_moments(session)
        all_moments.extend(moments)
        print(f"      {session.name[:36]}: {len(moments)} moments")

    print(f"      Total extracted: {len(all_moments)}")
    print()

    # Format for Ollama
    print("[3/3] Formatting for Ollama...")
    training_data = format_as_ollama_training(all_moments)

    # Save JSONL
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"claudine_training_enhanced_{timestamp}.jsonl"

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"      Saved: {output_file.name}")
    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"Enhanced training data: {len(training_data)} examples")
    print(f"Ready for: ollama create claudine-learned -f Modelfile")
    print()

if __name__ == "__main__":
    main()

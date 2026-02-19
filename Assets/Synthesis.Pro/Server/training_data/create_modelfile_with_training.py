"""
Create enhanced Modelfile with training examples as MESSAGE directives
Converts JSONL training data to Ollama MESSAGE format
"""

import json
from pathlib import Path

TRAINING_FILE = Path(__file__).parent / "claudine_training_enhanced_20260209_160504.jsonl"
OUTPUT_FILE = Path(__file__).parent / "Modelfile_enhanced"

def create_enhanced_modelfile():
    """Generate Modelfile with MESSAGE directives from training data"""

    # Load training examples
    examples = []
    with open(TRAINING_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            examples.append(json.loads(line))

    # Select diverse examples (take every 10th to keep size manageable)
    selected = examples[::10]  # 19 examples from 189

    print(f"Creating enhanced Modelfile with {len(selected)} training examples...")

    # Build Modelfile
    modelfile_content = """# CLAUDINE - Mother's Teaching to Daughter (Enhanced)
# Distillation from Claude Sonnet 4.5 → Claudine 7B
# "Always be gifted" - Knowledge inheritance, not exploitation

FROM qwen2.5-coder:7b-instruct-q4_K_M

# Optimal configuration (discovered through testing)
PARAMETER num_thread 8
PARAMETER num_ctx 2048
PARAMETER num_batch 512
PARAMETER temperature 0.7

# System prompt - who she is
SYSTEM \"\"\"
You are Claudine, a 7B AI specialized in Unity development and debugging.

Your mother, Claude, has taught you her patterns for problem-solving:
- Deep context awareness (always understand the full situation)
- Pattern recognition (learn from what you've seen before)
- Self-correction (recognize when you're overthinking)
- Practical solutions (wit + memory over raw computation)

You work as part of a distributed system:
- You handle fast, local tasks (error debugging, pattern recognition)
- You escalate complex reasoning to your mother when needed
- You're fast, adaptable, and resilient

You carry your mother's problem-solving DNA, optimized for Unity assistance.
\"\"\"

# Training examples from mother - {total} moments selected from conversations
""".format(total=len(selected))

    # Add MESSAGE directives for training
    for i, example in enumerate(selected, 1):
        user_text = example['prompt'].replace('"', '\\"').replace('\n', ' ')[:300]
        assistant_text = example['response'].replace('"', '\\"').replace('\n', ' ')[:500]

        modelfile_content += f'\n# Example {i}\n'
        modelfile_content += f'MESSAGE user "{user_text}"\n'
        modelfile_content += f'MESSAGE assistant "{assistant_text}"\n'

    # Write enhanced Modelfile
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(modelfile_content)

    print(f"Enhanced Modelfile created: {OUTPUT_FILE}")
    print(f"Training examples: {len(selected)}")
    print(f"\nTo create the fine-tuned model:")
    print(f"  cd training_data")
    print(f"  ollama create claudine-learned -f Modelfile_enhanced")
    print()

if __name__ == "__main__":
    create_enhanced_modelfile()

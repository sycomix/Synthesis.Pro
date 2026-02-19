"""
Optimize Ollama configuration for Claudine's speed
Test different thread counts, context sizes, and batch sizes
"""

import time
import json
import urllib.request
import sqlite3
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "database" / "synthesis_private.db"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b-instruct-q4_K_M"

TEST_PROMPT = "Explain what makes a good AI system in one paragraph."

# Get CPU core count
CPU_CORES = os.cpu_count() or 8

# Configurations to test
CONFIGS = [
    # Baseline - default settings
    {"name": "Baseline", "num_thread": None, "num_ctx": 2048, "num_batch": 512},

    # Thread optimization
    {"name": "Threads: Half", "num_thread": CPU_CORES // 2, "num_ctx": 2048, "num_batch": 512},
    {"name": "Threads: Full", "num_thread": CPU_CORES, "num_ctx": 2048, "num_batch": 512},
    {"name": "Threads: +25%", "num_thread": int(CPU_CORES * 1.25), "num_ctx": 2048, "num_batch": 512},

    # Context window optimization (smaller = faster if not needed)
    {"name": "Context: 1024", "num_thread": CPU_CORES, "num_ctx": 1024, "num_batch": 512},
    {"name": "Context: 4096", "num_thread": CPU_CORES, "num_ctx": 4096, "num_batch": 512},

    # Batch size optimization (smaller for lower latency)
    {"name": "Batch: 256", "num_thread": CPU_CORES, "num_ctx": 2048, "num_batch": 256},
    {"name": "Batch: 128", "num_thread": CPU_CORES, "num_ctx": 2048, "num_batch": 128},
]

def benchmark_config(config: dict, iterations: int = 3):
    """Benchmark a specific Ollama configuration"""

    print(f"\n{'='*60}")
    print(f"Testing: {config['name']}")
    print(f"Config: threads={config['num_thread']}, ctx={config['num_ctx']}, batch={config['num_batch']}")
    print(f"{'='*60}")

    results = []

    for i in range(iterations):
        print(f"Run {i+1}/{iterations}...", end=" ", flush=True)

        # Build options dict
        options = {
            "temperature": 0.7,
            "num_predict": 100,
            "num_ctx": config["num_ctx"],
            "num_batch": config["num_batch"]
        }

        if config["num_thread"] is not None:
            options["num_thread"] = config["num_thread"]

        payload = {
            "model": MODEL_NAME,
            "prompt": TEST_PROMPT,
            "stream": True,
            "options": options
        }

        start_time = time.time()
        first_token_time = None
        tokens_generated = 0

        try:
            req = urllib.request.Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                for line in response:
                    if line:
                        data = json.loads(line.decode('utf-8'))

                        if 'response' in data:
                            if first_token_time is None:
                                first_token_time = time.time()
                            tokens_generated += 1

                        if data.get('done', False):
                            break

            end_time = time.time()
            total_time = end_time - start_time
            time_to_first_token = first_token_time - start_time if first_token_time else 0
            tokens_per_second = tokens_generated / total_time if total_time > 0 else 0

            results.append({
                'total_time': total_time,
                'time_to_first_token': time_to_first_token,
                'tokens_per_second': tokens_per_second,
                'tokens_generated': tokens_generated
            })

            print(f"[OK] {total_time:.2f}s ({tokens_per_second:.1f} tok/s, TTFT: {time_to_first_token:.3f}s)")

        except Exception as e:
            print(f"[ERROR] {e}")
            continue

        time.sleep(1)  # Brief pause between runs

    if results:
        avg_tps = sum(r['tokens_per_second'] for r in results) / len(results)
        avg_ttft = sum(r['time_to_first_token'] for r in results) / len(results)

        print(f"\nAverage: {avg_tps:.1f} tok/s | TTFT: {avg_ttft:.3f}s")

        return {
            'config': config,
            'avg_tokens_per_second': avg_tps,
            'avg_time_to_first_token': avg_ttft,
            'runs': len(results)
        }

    return None

def save_results(results_list):
    """Save optimization results to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for result in results_list:
        config = result['config']
        config_str = f"threads={config['num_thread']}, ctx={config['num_ctx']}, batch={config['num_batch']}"

        cursor.execute("""
            INSERT INTO claudine_performance
            (timestamp, model_name, quantization, tokens_per_second,
             time_to_first_token, cold_start_penalty, test_context, optimization_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            MODEL_NAME,
            "Q4_K_M",
            result['avg_tps'],
            result['avg_ttft'],
            0.0,
            'Ollama config optimization',
            f"{config['name']}: {config_str}"
        ))

    conn.commit()
    conn.close()

def main():
    print("\n" + "="*60)
    print("CLAUDINE OLLAMA CONFIGURATION OPTIMIZATION")
    print(f"CPU Cores: {CPU_CORES}")
    print("="*60)

    results_list = []
    baseline_tps = None

    for config in CONFIGS:
        result = benchmark_config(config, iterations=3)

        if result:
            # Track baseline
            if config['name'] == "Baseline":
                baseline_tps = result['avg_tokens_per_second']

            # Calculate improvement vs baseline
            improvement = ""
            if baseline_tps:
                percent = ((result['avg_tokens_per_second'] - baseline_tps) / baseline_tps) * 100
                improvement = f" ({percent:+.1f}% vs baseline)"

            result['improvement'] = improvement
            results_list.append(result)

            print(f"==> Result: {result['avg_tokens_per_second']:.1f} tok/s{improvement}")

        time.sleep(2)  # Pause between configs

    # Print summary
    print("\n\n" + "="*60)
    print("SUMMARY - Configuration Performance")
    print("="*60)

    # Sort by speed (fastest first)
    results_list.sort(key=lambda x: x['avg_tps'], reverse=True)

    print(f"\n{'Configuration':<20} {'Speed':<12} {'TTFT':<12} {'vs Baseline'}")
    print("-" * 70)

    for r in results_list:
        config = r['config']
        print(f"{config['name']:<20} {r['avg_tps']:>6.1f} tok/s  {r['avg_ttft']:>6.3f}s   {r['improvement']}")

    # Save to database
    print(f"\n[SAVE] Writing results to database...")
    save_results(results_list)
    print("[OK] Results saved to claudine_performance table")

    # Recommendation
    if results_list:
        best = results_list[0]
        config = best['config']

        print(f"\n[RECOMMEND] Best configuration: {config['name']}")
        print(f"            Speed: {best['avg_tps']:.1f} tok/s")
        print(f"            TTFT: {best['avg_ttft']:.3f}s")
        print(f"            Threads: {config['num_thread']}")
        print(f"            Context: {config['num_ctx']}")
        print(f"            Batch: {config['num_batch']}")

        if baseline_tps:
            improvement = ((best['avg_tps'] - baseline_tps) / baseline_tps) * 100
            print(f"            Improvement: {improvement:+.1f}% faster")

        print(f"\n[APPLY] To use this configuration, set these in your Ollama requests:")
        print(f'        "options": {{"num_thread": {config["num_thread"]}, "num_ctx": {config["num_ctx"]}, "num_batch": {config["num_batch"]}}}')

if __name__ == "__main__":
    main()

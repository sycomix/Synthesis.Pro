"""
Save Claudine's configuration optimization results to database
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "database" / "synthesis_private.db"

def save_optimization():
    """Save the 8-thread optimization result"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Save the winning configuration
    cursor.execute("""
        INSERT INTO claudine_performance
        (timestamp, model_name, quantization, tokens_per_second,
         time_to_first_token, cold_start_penalty, test_context, optimization_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        "qwen2.5-coder:7b-instruct-q4_K_M",
        "Q4_K_M",
        7.9,  # Optimized speed
        2.896,  # Optimized TTFT
        0.0,
        "Configuration optimization - 8 threads",
        "OPTIMAL: num_thread=8, num_ctx=2048, num_batch=512 | +4.6% improvement over baseline"
    ))

    # Update her profile
    cursor.execute("""
        UPDATE claudine_profile
        SET current_tokens_per_second = ?,
            best_tokens_per_second = ?,
            total_optimizations = total_optimizations + 1,
            last_updated = ?,
            notes = ?
        WHERE name = 'Claudine'
    """, (
        7.9,  # Current (optimized)
        7.9,  # Best achieved
        datetime.now().isoformat(),
        "Optimized with 8 threads (+4.6%). Training curriculum prepared (6 examples). Ready for fine-tuning."
    ))

    conn.commit()
    conn.close()

    print("[OK] Optimization results saved to database")
    print("     Claudine: 7.5 -> 7.9 tok/s (+4.6%)")
    print("     Config: 8 threads, 2048 ctx, 512 batch")
    print("     Status: Ready for deployment")

if __name__ == "__main__":
    save_optimization()

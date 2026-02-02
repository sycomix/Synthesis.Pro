"""
Performance Monitor for Detective Mode
Tracks timing, memory usage, and performance metrics
"""

import time
import psutil
import os
from typing import Dict, List, Optional
from collections import defaultdict, deque
from datetime import datetime


class PerformanceMonitor:
    """
    Monitors performance metrics for Detective Mode operations.
    Tracks timing, memory usage, and provides performance reports.
    """

    def __init__(self, max_history: int = 100):
        """
        Initialize Performance Monitor.

        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self.timings = defaultdict(lambda: deque(maxlen=max_history))
        self.counters = defaultdict(int)
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        self.start_memory = self.get_memory_usage()

    def get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.

        Returns:
            Memory usage in MB
        """
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except:
            return 0.0

    def start_timer(self, operation: str) -> float:
        """
        Start timing an operation.

        Args:
            operation: Name of the operation

        Returns:
            Start timestamp
        """
        return time.time()

    def end_timer(self, operation: str, start_time: float) -> float:
        """
        End timing an operation and record the duration.

        Args:
            operation: Name of the operation
            start_time: Start timestamp from start_timer()

        Returns:
            Duration in seconds
        """
        duration = time.time() - start_time
        self.timings[operation].append(duration)
        self.counters[f"{operation}_count"] += 1
        return duration

    def time_operation(self, operation: str):
        """
        Context manager for timing operations.

        Usage:
            with monitor.time_operation("error_parsing"):
                # ... do work ...
        """
        class TimerContext:
            def __init__(self, monitor, operation):
                self.monitor = monitor
                self.operation = operation
                self.start = None

            def __enter__(self):
                self.start = self.monitor.start_timer(self.operation)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.monitor.end_timer(self.operation, self.start)

        return TimerContext(self, operation)

    def increment_counter(self, counter: str, amount: int = 1):
        """
        Increment a counter.

        Args:
            counter: Counter name
            amount: Amount to increment
        """
        self.counters[counter] += amount

    def get_avg_time(self, operation: str) -> float:
        """
        Get average time for an operation.

        Args:
            operation: Operation name

        Returns:
            Average time in seconds
        """
        times = self.timings.get(operation, [])
        if not times:
            return 0.0
        return sum(times) / len(times)

    def get_min_time(self, operation: str) -> float:
        """
        Get minimum time for an operation.

        Args:
            operation: Operation name

        Returns:
            Minimum time in seconds
        """
        times = self.timings.get(operation, [])
        if not times:
            return 0.0
        return min(times)

    def get_max_time(self, operation: str) -> float:
        """
        Get maximum time for an operation.

        Args:
            operation: Operation name

        Returns:
            Maximum time in seconds
        """
        times = self.timings.get(operation, [])
        if not times:
            return 0.0
        return max(times)

    def get_total_time(self, operation: str) -> float:
        """
        Get total time spent on an operation.

        Args:
            operation: Operation name

        Returns:
            Total time in seconds
        """
        times = self.timings.get(operation, [])
        if not times:
            return 0.0
        return sum(times)

    def get_counter(self, counter: str) -> int:
        """
        Get counter value.

        Args:
            counter: Counter name

        Returns:
            Counter value
        """
        return self.counters.get(counter, 0)

    def check_performance_target(self, operation: str, target_ms: float) -> bool:
        """
        Check if operation meets performance target.

        Args:
            operation: Operation name
            target_ms: Target time in milliseconds

        Returns:
            True if average time is below target
        """
        avg_time = self.get_avg_time(operation)
        return (avg_time * 1000) <= target_ms

    def get_performance_report(self) -> str:
        """
        Generate performance report.

        Returns:
            Performance report as string
        """
        current_memory = self.get_memory_usage()
        memory_delta = current_memory - self.start_memory
        uptime = time.time() - self.start_time

        report = []
        report.append("=" * 70)
        report.append("DETECTIVE MODE - PERFORMANCE REPORT")
        report.append("=" * 70)
        report.append(f"Uptime: {uptime:.2f}s")
        report.append(f"Memory: {current_memory:.2f} MB (delta: {memory_delta:+.2f} MB)")
        report.append("")

        # Operation timings
        if self.timings:
            report.append("OPERATION TIMINGS")
            report.append("-" * 70)
            report.append(f"{'Operation':<30} {'Avg (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12} {'Count':<8}")
            report.append("-" * 70)

            for operation in sorted(self.timings.keys()):
                avg_ms = self.get_avg_time(operation) * 1000
                min_ms = self.get_min_time(operation) * 1000
                max_ms = self.get_max_time(operation) * 1000
                count = len(self.timings[operation])

                report.append(f"{operation:<30} {avg_ms:<12.2f} {min_ms:<12.2f} {max_ms:<12.2f} {count:<8}")

            report.append("")

        # Performance targets
        report.append("PERFORMANCE TARGETS")
        report.append("-" * 70)

        targets = {
            'log_monitoring': 100,
            'error_parsing': 50,
            'kb_search': 200,
            'investigation': 1500,
        }

        for operation, target_ms in targets.items():
            if operation in self.timings:
                avg_ms = self.get_avg_time(operation) * 1000
                status = "OK" if avg_ms <= target_ms else "SLOW"
                report.append(f"{operation:<30} {avg_ms:>8.2f} ms / {target_ms:>8.0f} ms  [{status}]")
            else:
                report.append(f"{operation:<30} {'N/A':>8} / {target_ms:>8.0f} ms  [-]")

        report.append("")

        # Counters
        if self.counters:
            report.append("COUNTERS")
            report.append("-" * 70)
            for counter in sorted(self.counters.keys()):
                if not counter.endswith('_count'):  # Skip auto-generated count counters
                    value = self.counters[counter]
                    report.append(f"{counter:<40} {value:>10}")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)

    def get_metrics_summary(self) -> Dict:
        """
        Get metrics as dictionary for programmatic access.

        Returns:
            Dict with all metrics
        """
        return {
            'uptime': time.time() - self.start_time,
            'memory_mb': self.get_memory_usage(),
            'memory_delta_mb': self.get_memory_usage() - self.start_memory,
            'timings': {
                op: {
                    'avg_ms': self.get_avg_time(op) * 1000,
                    'min_ms': self.get_min_time(op) * 1000,
                    'max_ms': self.get_max_time(op) * 1000,
                    'count': len(self.timings[op])
                }
                for op in self.timings.keys()
            },
            'counters': dict(self.counters)
        }

    def reset(self):
        """Reset all metrics."""
        self.timings.clear()
        self.counters.clear()
        self.start_time = time.time()
        self.start_memory = self.get_memory_usage()


# Global performance monitor instance
_global_monitor = None


def get_global_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor

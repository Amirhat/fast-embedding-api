"""Benchmarking suite for Fast Embedding API."""

import asyncio
import time
import statistics
from typing import List, Dict
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# Configuration
BASE_URL = "http://localhost:8000"
MODEL_NAME = "BAAI/bge-small-en-v1.5"


class BenchmarkRunner:
    """Run performance benchmarks for the API."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = {}

    def benchmark_single_embedding(
        self, num_requests: int = 100, text_length: int = 100
    ) -> Dict:
        """Benchmark single embedding requests."""
        print(f"\n🔥 Benchmarking single embeddings ({num_requests} requests)...")

        text = "word " * (text_length // 5)
        times = []

        for i in range(num_requests):
            start = time.time()
            response = requests.post(
                f"{self.base_url}/embed",
                json={"model_name": MODEL_NAME, "text": text},
            )
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                times.append(elapsed)
            else:
                print(f"Error on request {i}: {response.status_code}")

            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{num_requests}")

        return {
            "test": "single_embedding",
            "num_requests": num_requests,
            "text_length": text_length,
            "avg_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p95_ms": (
                statistics.quantiles(times, n=20)[18] if len(times) > 20 else max(times)
            ),
            "p99_ms": (
                statistics.quantiles(times, n=100)[98]
                if len(times) > 100
                else max(times)
            ),
            "requests_per_sec": 1000 / statistics.mean(times),
        }

    def benchmark_batch_embedding(
        self, num_requests: int = 50, batch_size: int = 10, text_length: int = 100
    ) -> Dict:
        """Benchmark batch embedding requests."""
        print(
            f"\n🚀 Benchmarking batch embeddings ({num_requests} requests, batch size {batch_size})..."
        )

        text = "word " * (text_length // 5)
        texts = [text] * batch_size
        times = []

        for i in range(num_requests):
            start = time.time()
            response = requests.post(
                f"{self.base_url}/embed/batch",
                json={"model_name": MODEL_NAME, "texts": texts},
            )
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                times.append(elapsed)
            else:
                print(f"Error on request {i}: {response.status_code}")

            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{num_requests}")

        avg_time = statistics.mean(times)
        avg_per_text = avg_time / batch_size

        return {
            "test": "batch_embedding",
            "num_requests": num_requests,
            "batch_size": batch_size,
            "text_length": text_length,
            "avg_ms": avg_time,
            "avg_ms_per_text": avg_per_text,
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p95_ms": (
                statistics.quantiles(times, n=20)[18] if len(times) > 20 else max(times)
            ),
            "requests_per_sec": 1000 / avg_time,
            "embeddings_per_sec": (1000 / avg_time) * batch_size,
        }

    def benchmark_concurrent_requests(
        self, num_requests: int = 100, concurrency: int = 10, text_length: int = 100
    ) -> Dict:
        """Benchmark concurrent requests."""
        print(
            f"\n⚡ Benchmarking concurrent requests ({num_requests} total, {concurrency} concurrent)..."
        )

        text = "word " * (text_length // 5)
        times = []

        def make_request(i: int):
            start = time.time()
            response = requests.post(
                f"{self.base_url}/embed",
                json={"model_name": MODEL_NAME, "text": text},
            )
            elapsed = (time.time() - start) * 1000
            return elapsed if response.status_code == 200 else None

        start_total = time.time()
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]

            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                if result:
                    times.append(result)

                if (i + 1) % 10 == 0:
                    print(f"  Completed {i + 1}/{num_requests}")

        total_time = (time.time() - start_total) * 1000

        return {
            "test": "concurrent_requests",
            "num_requests": num_requests,
            "concurrency": concurrency,
            "text_length": text_length,
            "total_time_ms": total_time,
            "avg_request_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "p95_ms": (
                statistics.quantiles(times, n=20)[18] if len(times) > 20 else max(times)
            ),
            "throughput_rps": (num_requests / total_time) * 1000,
        }

    def benchmark_text_sizes(self, sizes: List[int] = None) -> Dict:
        """Benchmark different text sizes."""
        if sizes is None:
            sizes = [50, 100, 500, 1000, 2000, 4000]

        print(f"\n📏 Benchmarking different text sizes...")

        results = []
        for size in sizes:
            text = "word " * (size // 5)
            times = []

            for _ in range(20):
                start = time.time()
                response = requests.post(
                    f"{self.base_url}/embed",
                    json={"model_name": MODEL_NAME, "text": text},
                )
                elapsed = (time.time() - start) * 1000

                if response.status_code == 200:
                    times.append(elapsed)

            results.append(
                {
                    "text_length": size,
                    "avg_ms": statistics.mean(times),
                    "median_ms": statistics.median(times),
                }
            )

            print(f"  {size} chars: {statistics.mean(times):.2f}ms avg")

        return {"test": "text_sizes", "results": results}

    def benchmark_cache_performance(self) -> Dict:
        """Benchmark model caching performance."""
        print(f"\n💾 Benchmarking cache performance...")

        # First request (cold cache)
        text = "test cache performance"

        print("  Testing cold cache (first load)...")
        start = time.time()
        response = requests.post(
            f"{self.base_url}/embed",
            json={"model_name": MODEL_NAME, "text": text},
        )
        cold_time = (time.time() - start) * 1000

        # Subsequent requests (warm cache)
        print("  Testing warm cache...")
        warm_times = []
        for _ in range(50):
            start = time.time()
            response = requests.post(
                f"{self.base_url}/embed",
                json={"model_name": MODEL_NAME, "text": text},
            )
            elapsed = (time.time() - start) * 1000
            warm_times.append(elapsed)

        return {
            "test": "cache_performance",
            "cold_cache_ms": cold_time,
            "warm_cache_avg_ms": statistics.mean(warm_times),
            "speedup": cold_time / statistics.mean(warm_times),
        }

    def run_all_benchmarks(self) -> Dict:
        """Run all benchmarks and return results."""
        print("=" * 60)
        print("Fast Embedding API - Performance Benchmark")
        print("=" * 60)

        # Check if API is running
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code != 200:
                print("❌ API is not responding. Please start the server first.")
                return {}
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Please start the server first.")
            return {}

        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_url": self.base_url,
            "model": MODEL_NAME,
            "benchmarks": {},
        }

        # Run benchmarks
        results["benchmarks"]["single_embedding"] = self.benchmark_single_embedding(
            num_requests=100
        )
        results["benchmarks"]["batch_embedding"] = self.benchmark_batch_embedding(
            num_requests=50, batch_size=10
        )
        results["benchmarks"]["concurrent_requests"] = (
            self.benchmark_concurrent_requests(num_requests=100, concurrency=10)
        )
        results["benchmarks"]["text_sizes"] = self.benchmark_text_sizes()
        results["benchmarks"]["cache_performance"] = self.benchmark_cache_performance()

        # Calculate comparison
        single_avg = results["benchmarks"]["single_embedding"]["avg_ms"]
        batch_avg_per_text = results["benchmarks"]["batch_embedding"]["avg_ms_per_text"]
        speedup = single_avg / batch_avg_per_text

        results["comparison"] = {
            "single_vs_batch_speedup": speedup,
            "batch_efficiency": f"{speedup:.1f}x faster per text",
        }

        return results

    def print_summary(self, results: Dict):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("📊 BENCHMARK RESULTS SUMMARY")
        print("=" * 60)

        # Single Embedding
        single = results["benchmarks"]["single_embedding"]
        print(f"\n1️⃣  Single Embedding Performance:")
        print(f"   Average: {single['avg_ms']:.2f}ms")
        print(f"   Median:  {single['median_ms']:.2f}ms")
        print(f"   P95:     {single['p95_ms']:.2f}ms")
        print(f"   Throughput: {single['requests_per_sec']:.1f} req/s")

        # Batch Embedding
        batch = results["benchmarks"]["batch_embedding"]
        print(f"\n2️⃣  Batch Embedding Performance (batch size {batch['batch_size']}):")
        print(f"   Average per batch: {batch['avg_ms']:.2f}ms")
        print(f"   Average per text:  {batch['avg_ms_per_text']:.2f}ms")
        print(f"   Throughput: {batch['embeddings_per_sec']:.1f} embeddings/s")

        # Concurrent
        concurrent = results["benchmarks"]["concurrent_requests"]
        print(f"\n3️⃣  Concurrent Requests (concurrency {concurrent['concurrency']}):")
        print(f"   Average latency: {concurrent['avg_request_ms']:.2f}ms")
        print(f"   Throughput: {concurrent['throughput_rps']:.1f} req/s")

        # Cache
        cache = results["benchmarks"]["cache_performance"]
        print(f"\n4️⃣  Cache Performance:")
        print(f"   Cold cache: {cache['cold_cache_ms']:.2f}ms")
        print(f"   Warm cache: {cache['warm_cache_avg_ms']:.2f}ms")
        print(f"   Speedup: {cache['speedup']:.1f}x faster")

        # Comparison
        print(f"\n🚀 Batch vs Single:")
        print(f"   Speedup: {results['comparison']['single_vs_batch_speedup']:.1f}x")
        print(f"   {results['comparison']['batch_efficiency']}")

        print("\n" + "=" * 60)

    def save_results(self, results: Dict, filename: str = "benchmark_results.json"):
        """Save results to JSON file."""
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")


def main():
    """Main benchmark execution."""
    runner = BenchmarkRunner()
    results = runner.run_all_benchmarks()

    if results:
        runner.print_summary(results)
        runner.save_results(results, "benchmarks/benchmark_results.json")


if __name__ == "__main__":
    main()

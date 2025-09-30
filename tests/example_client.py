"""Example client for the Fast Embedding API."""

import requests
import json
import time


def main():
    """Demonstrate using the embedding API with all features."""
    base_url = "http://localhost:8000"

    print("=" * 60)
    print("Fast Embedding API - Client Examples")
    print("=" * 60)
    print()

    # 1. Check health
    print("1. Health Check")
    print("-" * 40)
    response = requests.get(f"{base_url}/health")
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

    # 2. List available models
    print("2. Available Models")
    print("-" * 40)
    response = requests.get(f"{base_url}/models")
    print(json.dumps(response.json(), indent=2))
    print()

    # 3. Single embedding
    print("3. Single Embedding")
    print("-" * 40)
    model_name = "BAAI/bge-small-en-v1.5"
    text = "The quick brown fox jumps over the lazy dog"

    start_time = time.time()
    response = requests.post(
        f"{base_url}/embed", json={"model_name": model_name, "text": text}
    )
    elapsed = (time.time() - start_time) * 1000

    if response.status_code == 200:
        result = response.json()
        print(f"Text: {text}")
        print(f"Model: {result['model_name']}")
        print(f"Dimension: {result['dimension']}")
        print(f"Processing Time: {result['processing_time_ms']}ms")
        print(f"Total Time (including network): {elapsed:.2f}ms")
        print(f"First 5 values: {result['embedding'][:5]}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    print()

    # 4. Batch embeddings (more efficient)
    print("4. Batch Embeddings (Efficient!)")
    print("-" * 40)
    texts = [
        "Machine learning is transforming the world",
        "Python is a great programming language",
        "Embeddings capture semantic meaning",
        "Deep learning powers modern AI",
        "Natural language processing enables understanding",
    ]

    start_time = time.time()
    response = requests.post(
        f"{base_url}/embed/batch", json={"model_name": model_name, "texts": texts}
    )
    batch_elapsed = (time.time() - start_time) * 1000

    if response.status_code == 200:
        result = response.json()
        print(f"Batch size: {result['count']}")
        print(f"Dimension: {result['dimension']}")
        print(f"Processing Time: {result['processing_time_ms']}ms")
        print(f"Total Time: {batch_elapsed:.2f}ms")
        print(f"Time per embedding: {batch_elapsed / len(texts):.2f}ms")
        print()
        for i, (text, embedding) in enumerate(zip(texts, result["embeddings"]), 1):
            print(f"  {i}. {text[:50]}...")
            print(f"     First 3 values: {embedding[:3]}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    print()

    # 5. Compare single vs batch performance
    print("5. Performance Comparison: Single vs Batch")
    print("-" * 40)

    # Single requests
    single_start = time.time()
    for text in texts[:3]:  # Just 3 for demo
        requests.post(
            f"{base_url}/embed", json={"model_name": model_name, "text": text}
        )
    single_time = (time.time() - single_start) * 1000

    # Batch request
    batch_start = time.time()
    requests.post(
        f"{base_url}/embed/batch",
        json={"model_name": model_name, "texts": texts[:3]},
    )
    batch_time = (time.time() - batch_start) * 1000

    print(f"3 texts via single requests: {single_time:.2f}ms")
    print(f"3 texts via batch request: {batch_time:.2f}ms")
    print(f"Speedup: {single_time / batch_time:.2f}x faster")
    print()

    # 6. Model information
    print("6. Model Information")
    print("-" * 40)
    response = requests.get(f"{base_url}/models/{model_name}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    print()

    # 7. Check metrics
    print("7. API Metrics")
    print("-" * 40)
    response = requests.get(f"{base_url}/metrics")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    elif response.status_code == 403:
        print("Metrics are disabled in configuration")
    else:
        print(f"Error: {response.status_code}")
    print()

    # 8. Cache status after all operations
    print("8. Final Cache Status")
    print("-" * 40)
    response = requests.get(f"{base_url}/health")
    if response.status_code == 200:
        result = response.json()
        cache_info = result["cache_info"]
        print(f"Cached models: {cache_info['cached_models']}")
        print(f"Number cached: {cache_info['num_cached']}/{cache_info['max_cached']}")
        print(f"Cache TTL: {cache_info['cache_ttl']} seconds")
        print(f"API Uptime: {result['uptime_seconds']} seconds")
    print()

    # 9. Error handling examples
    print("9. Error Handling Examples")
    print("-" * 40)

    # Invalid model name (if allowed_models is set)
    print("Testing invalid model name...")
    response = requests.post(
        f"{base_url}/embed",
        json={"model_name": "invalid/model", "text": "test"},
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.json().get('detail', 'Unknown error')}")
    print()

    # Empty text
    print("Testing empty text...")
    response = requests.post(
        f"{base_url}/embed", json={"model_name": model_name, "text": ""}
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.json().get('detail', 'Unknown error')}")
    print()

    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

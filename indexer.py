#!/usr/bin/env python3
"""
Enterprise Elasticsearch Resilient Bulk Indexer
Features exponential backoff retry logic, HTTP 429 / 503 queue-pressure mitigation,
chunked streaming batches, and real-time indexing performance telemetry.
"""

import sys
import json
import time
import uuid
import random
import urllib.request
import urllib.error
from datetime import datetime, timezone

CATEGORIES = ["Infrastructure", "Observability", "Databases", "Networking", "Security"]
SAMPLE_TITLES = [
    "Production Kubernetes Operator Handbook",
    "Distributed Tracing with OpenTelemetry and Jaeger",
    "Elasticsearch Scalability and Custom Analyzers",
    "Real-Time Stream Processing with Apache Kafka",
    "Zero-Trust Cloud Network Security Architectures",
    "Site Reliability Engineering (SRE) Incident Management",
    "Multi-Cloud FinOps and Resource Optimization"
]

def generate_sample_documents(count=1000):
    docs = []
    for _ in range(count):
        title = random.choice(SAMPLE_TITLES)
        doc = {
            "id": str(uuid.uuid4()),
            "title": f"{title} #{random.randint(100, 999)}",
            "description": f"<p>Comprehensive guide covering <b>{title}</b> with enterprise architectural patterns, SRE reliability practices, and hands-on implementations.</p>",
            "category": random.choice(CATEGORIES),
            "tags": ["cloud-native", "devops", "enterprise"],
            "price": round(random.uniform(29.99, 149.99), 2),
            "rating": round(random.uniform(4.0, 5.0), 1),
            "in_stock": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        docs.append(doc)
    return docs

def format_bulk_ndjson(docs, index_name="search_index"):
    lines = []
    for doc in docs:
        action = {"index": {"_index": index_name, "_id": doc["id"]}}
        lines.append(json.dumps(action))
        lines.append(json.dumps(doc))
    return "\n".join(lines) + "\n"

def execute_bulk_request_with_backoff(es_url, ndjson_payload, max_retries=5, initial_backoff=1.0, backoff_factor=2.0):
    url = f"{es_url.rstrip('/')}/_bulk"
    headers = {"Content-Type": "application/x-ndjson"}
    data = ndjson_payload.encode("utf-8")

    current_backoff = initial_backoff
    for attempt in range(1, max_retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            start_t = time.perf_counter()
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = json.loads(resp.read().decode("utf-8"))
                duration = time.perf_counter() - start_t
                
                # Check for item-level rejections (e.g. 429 inside bulk response)
                if resp_body.get("errors"):
                    items = resp_body.get("items", [])
                    rejected = [item for item in items if item.get("index", {}).get("status") in (429, 503)]
                    if rejected and attempt < max_retries:
                        jitter = random.uniform(0.1, 0.5)
                        sleep_time = current_backoff + jitter
                        print(f"[WARN] Attempt {attempt}: {len(rejected)} items rejected with queue pressure. Backing off {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                        current_backoff *= backoff_factor
                        continue
                return True, duration, len(data)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < max_retries:
                jitter = random.uniform(0.1, 0.5)
                sleep_time = current_backoff + jitter
                print(f"[WARN] HTTP {e.code} received from Elasticsearch cluster. Retrying in {sleep_time:.2f}s (Attempt {attempt}/{max_retries})...")
                time.sleep(sleep_time)
                current_backoff *= backoff_factor
            else:
                print(f"[ERROR] HTTP request failed with status {e.code}: {e.reason}")
                return False, 0, 0
        except Exception as e:
            if attempt < max_retries:
                time.sleep(current_backoff)
                current_backoff *= backoff_factor
            else:
                print(f"[ERROR] Connection failed: {e}")
                return False, 0, 0

    return False, 0, 0

def bulk_index(docs, es_url="http://localhost:9200", index_name="search_index", chunk_size=200):
    print("=" * 65)
    print("      Elasticsearch Resilient Bulk Ingestion Engine          ")
    print("=" * 65)
    print(f"Cluster URL:    {es_url}")
    print(f"Target Index:   {index_name}")
    print(f"Total Docs:     {len(docs):,}")
    print(f"Batch Chunk:    {chunk_size} docs/batch")
    print("-" * 65)

    total_indexed = 0
    total_bytes = 0
    total_time = 0.0

    chunks = [docs[i:i + chunk_size] for i in range(0, len(docs), chunk_size)]
    for idx, chunk in enumerate(chunks, 1):
        ndjson = format_bulk_ndjson(chunk, index_name=index_name)
        success, duration, bytes_sent = execute_bulk_request_with_backoff(es_url, ndjson)
        if success:
            total_indexed += len(chunk)
            total_bytes += bytes_sent
            total_time += duration
            print(f"[*] Processed chunk {idx}/{len(chunks)} ({len(chunk)} docs) in {duration*1000:.1f}ms")
        else:
            print(f"[FAIL] Chunk {idx}/{len(chunks)} failed after maximum retries.")

    throughput = total_indexed / total_time if total_time > 0 else 0
    mb_rate = (total_bytes / (1024 * 1024)) / total_time if total_time > 0 else 0

    print("=" * 65)
    print("📊 Bulk Indexing Summary:")
    print(f"  • Successfully Indexed: {total_indexed:,} documents")
    print(f"  • Elapsed Indexing Time: {total_time:.2f} seconds")
    print(f"  • Indexing Throughput:   {throughput:,.1f} docs/sec")
    print(f"  • Data Ingestion Rate:   {mb_rate:.2f} MB/sec")
    print("=" * 65)
    return total_indexed

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:9200"
    num_docs = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    sample_data = generate_sample_documents(num_docs)
    bulk_index(sample_data, es_url=url, index_name="search_index")

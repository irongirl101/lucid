
# Node 1 - Data Ingestion

## Overview
Node 1 handles data ingestion and validation for the
Distributed Search Engine project.

## Technologies Used
- Python 3.10
- PySpark 3.3.4
- Hadoop HDFS 3.3.6
- Apache Iceberg 1.8.1

## Implementation
1. Read input JSON files using Spark.
2. Reject malformed and incomplete records.
3. Remove duplicates by document ID.
4. Keep the latest document version.
5. Apply inserts, updates and deletes using Iceberg.
6. Remove links to nonexistent documents.
7. Track changes and Iceberg snapshots.
8. Avoid reprocessing completed phases.

## Input Files
- data/pages.jsonl - Phase 0
- data/changes.json - Phase 1

## Local Testing Results

| Metric | Phase 0 | Phase 1 |
|---|---|---|
| Documents | 1000 | 975 |
| Valid Links | 499 | 467 |
| Rejected Records | 20 | 0 |

Both phases were tested using local Spark and Iceberg.
The idempotency test also passed.


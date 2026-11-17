
# Distributed Search Engine - Node 4

**Student:** Prachi Ganesh Joshi  
**SRN:** PES1UG24CS325  
**Role:** Node 4 - Search Service and UI

## Overview

Node 4 provides the search interface and search API
for the distributed search engine.

## Technology Stack

- Python 3
- FastAPI
- Uvicorn
- Pandas
- PyArrow
- NumPy
- HTML, CSS and JavaScript

## Implemented Features

1. Custom BM25 search engine.
2. Tokenization and document frequency calculation.
3. Positive IDF scoring.
4. Document length normalization.
5. PageRank integration.
6. Combined BM25 and PageRank ranking.
7. FastAPI search endpoint.
8. HTML/CSS search interface.
9. Parquet export loader prototype.
10. Serving version manager prototype.

## Ranking Configuration

- BM25 k1 = 1.2
- BM25 b = 0.75
- BM25 weight = 0.7
- PageRank weight = 0.3

## Project Structure

```text
distributed-search-node4/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── search_engine.py
│   ├── sample_data.py
│   ├── ranking.py
│   ├── data_loader.py
│   └── version_manager.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── data/
├── test_search.py
├── test_ranking.py
├── test_node4.py
└── requirements.txt
```

## Run the Application

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

- http://127.0.0.1:8000/ui
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Current Development Status

The search service currently uses temporary sample
documents. Integration with Node 3's validated
Parquet export is pending.

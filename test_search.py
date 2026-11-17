from app.search_engine import SearchEngine
from app.sample_data import SAMPLE_DOCUMENTS


def main():
    engine = SearchEngine(
        SAMPLE_DOCUMENTS,
        k1=1.2,
        b=0.75
    )

    queries = [
        "distributed search engine",
        "BM25 ranking",
        "PageRank algorithm",
        "Apache Spark",
        "information retrieval"
    ]

    for query in queries:
        print("\n" + "=" * 65)
        print(f"QUERY: {query}")
        print("=" * 65)

        results = engine.search(query, top_k=5)

        if not results:
            print("No matching documents found.")
            continue

        for rank, result in enumerate(results, start=1):
            print(f"\nRank: {rank}")
            print(f"ID: {result['doc_id']}")
            print(f"Title: {result['title']}")
            print(f"BM25 Score: {result['bm25_score']:.4f}")
            print(f"URL: {result['url']}")


if __name__ == "__main__":
    main()

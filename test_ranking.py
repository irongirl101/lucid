
from app.search_engine import SearchEngine
from app.sample_data import SAMPLE_DOCUMENTS
from app.ranking import combine_scores


def main():
    engine = SearchEngine(SAMPLE_DOCUMENTS)

    queries = [
        "distributed search engine",
        "BM25 ranking",
        "PageRank algorithm",
        "Apache Spark"
    ]

    for query in queries:
        print("\n" + "=" * 70)
        print("QUERY:", query)
        print("=" * 70)

        bm25_results = engine.search(query, top_k=10)

        final_results = combine_scores(
            bm25_results,
            bm25_weight=0.7,
            pagerank_weight=0.3
        )

        for rank, result in enumerate(final_results, start=1):
            print(f"\nRank: {rank}")
            print("Document:", result["doc_id"])
            print("Title:", result["title"])
            print("BM25:", round(result["bm25_score"], 4))
            print("PageRank:", result["pagerank"])
            print("Normalized BM25:", round(result["normalized_bm25"], 4))
            print("Normalized PageRank:", round(result["normalized_pagerank"], 4))
            print("Final Score:", round(result["final_score"], 4))


if __name__ == "__main__":
    main()

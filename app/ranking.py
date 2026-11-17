
def combine_scores(results, bm25_weight=0.7, pagerank_weight=0.3):
    """
    Combine normalized BM25 and PageRank scores.

    Final Score =
        0.7 * (BM25 / maximum BM25)
        + 0.3 * (PageRank / maximum PageRank)
    """

    if not results:
        return []

    max_bm25 = max(
        (result.get("bm25_score", 0) for result in results),
        default=0
    )

    max_pagerank = max(
        (result.get("pagerank", 0) for result in results),
        default=0
    )

    ranked_results = []

    for result in results:
        bm25 = result.get("bm25_score", 0)
        pagerank = result.get("pagerank", 0)

        normalized_bm25 = (
            bm25 / max_bm25 if max_bm25 > 0 else 0
        )

        normalized_pagerank = (
            pagerank / max_pagerank if max_pagerank > 0 else 0
        )

        final_score = (
            bm25_weight * normalized_bm25
            + pagerank_weight * normalized_pagerank
        )

        item = result.copy()
        item["normalized_bm25"] = normalized_bm25
        item["normalized_pagerank"] = normalized_pagerank
        item["final_score"] = final_score

        ranked_results.append(item)

    ranked_results.sort(
        key=lambda item: item["final_score"],
        reverse=True
    )

    return ranked_results

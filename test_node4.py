from app.search_engine import SearchEngine
from app.sample_data import SAMPLE_DOCUMENTS
from app.ranking import combine_scores


def test_bm25_search():
    engine = SearchEngine(SAMPLE_DOCUMENTS)
    results = engine.search("BM25 ranking")

    assert len(results) > 0
    assert results[0]["doc_id"] == "DOC003"


def test_empty_query():
    engine = SearchEngine(SAMPLE_DOCUMENTS)
    assert engine.search("") == []


def test_unrelated_query():
    engine = SearchEngine(SAMPLE_DOCUMENTS)
    assert engine.search("quantum spaceship xyz") == []


def test_combined_ranking():
    engine = SearchEngine(SAMPLE_DOCUMENTS)
    results = engine.search("BM25 ranking")
    ranked = combine_scores(results)

    assert ranked[0]["doc_id"] == "DOC003"
    assert "final_score" in ranked[0]


def test_ranking_weights():
    engine = SearchEngine(SAMPLE_DOCUMENTS)
    results = combine_scores(engine.search("BM25 ranking"))

    assert all(0 <= item["final_score"] <= 1 for item in results)


if __name__ == "__main__":
    tests = [
        test_bm25_search,
        test_empty_query,
        test_unrelated_query,
        test_combined_ranking,
        test_ranking_weights
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print(f"\n{len(tests)} tests passed!")

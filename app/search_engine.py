
import re
import math
from collections import Counter


class SearchEngine:

    def __init__(self, documents, k1=1.2, b=0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b

        self.tokenized_corpus = [
            self.tokenize(doc["title"] + " " + doc["content"])
            for doc in documents
        ]

        self.total_documents = len(documents)

        # Calculate the length of each document
        self.doc_lengths = [
            len(tokens) for tokens in self.tokenized_corpus
        ]

        # Calculate average document length
        self.avg_doc_length = (
            sum(self.doc_lengths) / self.total_documents
            if self.total_documents > 0 else 0
        )

        # Calculate document frequency for each term
        self.doc_freq = Counter()

        for tokens in self.tokenized_corpus:
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freq[term] += 1

    @staticmethod
    def tokenize(text):
        """Convert text into lowercase alphanumeric tokens."""
        return re.findall(r"\b[a-z0-9]+\b", text.lower())

    def calculate_idf(self, term):
        """Calculate positive inverse document frequency."""
        df = self.doc_freq.get(term, 0)
        N = self.total_documents

        if N == 0 or df == 0:
            return 0.0

        return math.log(
            1 + (N - df + 0.5) / (df + 0.5)
        )

    def calculate_bm25(self, query_tokens, doc_index):
        """Calculate BM25 score for one document."""
        document_tokens = self.tokenized_corpus[doc_index]
        term_frequency = Counter(document_tokens)

        doc_length = self.doc_lengths[doc_index]
        score = 0.0

        for term in query_tokens:

            tf = term_frequency.get(term, 0)

            if tf == 0:
                continue

            idf = self.calculate_idf(term)

            numerator = tf * (self.k1 + 1)

            denominator = tf + self.k1 * (
                1 - self.b +
                self.b * doc_length / self.avg_doc_length
            ) if self.avg_doc_length > 0 else tf + self.k1

            score += idf * (numerator / denominator)

        return score

    def search(self, query, top_k=10):
        """Search documents and return ranked results."""

        query_tokens = self.tokenize(query)

        if not query_tokens or self.total_documents == 0:
            return []

        results = []

        for index, document in enumerate(self.documents):

            score = self.calculate_bm25(
                query_tokens,
                index
            )

            if score > 0:
                result = document.copy()
                result["bm25_score"] = float(score)
                results.append(result)

        results.sort(
            key=lambda item: item["bm25_score"],
            reverse=True
        )

        return results[:max(0, top_k)]

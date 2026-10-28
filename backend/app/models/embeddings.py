import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Any

class LightweightEmbeddingEngine:
    """
    Lightweight TF-IDF and character n-gram embedding engine
    providing semantic similarity vectors across clauses and reference benchmarks.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english', ngram_range=(1, 2))
        self.fitted = False

    def fit_and_transform(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 10))
        valid_texts = [t if t.strip() else "general contract terms" for t in texts]
        tfidf_matrix = self.vectorizer.fit_transform(valid_texts)
        self.fitted = True
        return tfidf_matrix.toarray()

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        if not self.fitted:
            self.fit_and_transform([text_a, text_b])
        v = self.vectorizer.transform([text_a, text_b]).toarray()
        dot_product = np.dot(v[0], v[1])
        norm_a = np.linalg.norm(v[0])
        norm_b = np.linalg.norm(v[1])
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot_product / (norm_a * norm_b))

embedding_engine = LightweightEmbeddingEngine()

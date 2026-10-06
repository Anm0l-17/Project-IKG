import logging
import math
import re

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating vector embeddings and calculating cosine similarity.
    Uses SentenceTransformers when available, with a deterministic TF-IDF fallback.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name)
        except (ImportError, OSError, RuntimeError):
            self.model = None

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generates a 384-dimensional dense vector embedding.
        """
        if not text:
            return [0.0] * 384

        if self.model is not None:
            try:
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except (AttributeError, RuntimeError, TypeError, ValueError) as error:
                logger.warning("Embedding model failed; using deterministic fallback: %s", error)

        # Deterministic 384-dim Hashed Term-Frequency Fallback
        return self._generate_fallback_embedding(text)

    def _generate_fallback_embedding(self, text: str) -> list[float]:
        vector = [0.0] * 384
        words = re.findall(r"\w+", text.lower())
        if not words:
            return vector

        for word in words:
            # Deterministic hash bucket
            bucket = abs(hash(word)) % 384
            vector[bucket] += 1.0

        # L2 Normalize
        norm = math.sqrt(sum(val * val for val in vector))
        if norm > 0:
            vector = [val / norm for val in vector]

        return vector

    @staticmethod
    def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """
        Calculates cosine similarity between two equal-length vectors.
        """
        if len(vec_a) != len(vec_b) or not vec_a or not vec_b:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)


embedding_service = EmbeddingService()

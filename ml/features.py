from enum import Enum
from typing import Optional

import huggingface_hub as hf
from sentence_transformers import SentenceTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, make_pipeline


class Features(Enum):
    TF_IDF = "tfidf"
    EMBEDDINGS = "embeddings"


class SentenceTransformerVectorizer(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        batch_size: int = 128,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.model = None

    def fit(self, X: str | list[str], y: Optional[list[int] | list[float]] = None):
        if self.model is None:
            try:
                self.model = SentenceTransformer(self.model_name, local_files_only=True)
            except:
                hf.snapshot_download(f"sentence-transformers/{self.model_name}")
                self.model = SentenceTransformer(self.model_name, local_files_only=True)

        return self

    def transform(self, X: str | list[str]):
        if self.model is None:
            raise RuntimeError("You must fit the vectorizer before calling transform")

        return self.model.encode(X, batch_size=self.batch_size)


def make_text_pipeline(features: Features) -> Pipeline:
    match features:
        case Features.TF_IDF:
            return make_pipeline(
                TfidfVectorizer(
                    max_features=10_000,
                    ngram_range=(1, 2),
                    stop_words="english",
                    lowercase=True,
                    max_df=0.95,
                    min_df=5,
                ),
            )
        case Features.EMBEDDINGS:
            return make_pipeline(
                SentenceTransformerVectorizer(),
            )

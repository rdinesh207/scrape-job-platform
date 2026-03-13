from __future__ import annotations

import logging

from openai import OpenAI

from app.config.settings import settings


logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAIAPIKEY is not configured.")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            text = "N/A"
        logger.info(
            "OpenAI embedding request model=%s input_len=%d",
            self.model,
            len(text),
        )
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        embedding = response.data[0].embedding
        logger.info(
            "OpenAI embedding success model=%s dims=%d",
            self.model,
            len(embedding),
        )
        return embedding

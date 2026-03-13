from __future__ import annotations

import logging

from openai import OpenAI

from app.config.settings import settings


logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAIAPIKEY is not configured.")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_llm

    def json_completion(self, prompt: str) -> str:
        logger.info(
            "OpenAI json_completion request model=%s prompt_len=%d",
            self.model,
            len(prompt),
        )
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                response_format={"type": "json_object"},
            )
        except TypeError:
            # Compatibility fallback for older OpenAI SDK versions.
            response = self.client.responses.create(
                model=self.model,
                input=f"{prompt}\nReturn valid JSON only.",
            )
        logger.info(
            "OpenAI json_completion success model=%s output_len=%d",
            self.model,
            len(response.output_text or ""),
        )
        return response.output_text

    def text_completion(self, prompt: str) -> str:
        logger.info(
            "OpenAI text_completion request model=%s prompt_len=%d",
            self.model,
            len(prompt),
        )
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        logger.info(
            "OpenAI text_completion success model=%s output_len=%d",
            self.model,
            len(response.output_text or ""),
        )
        return response.output_text

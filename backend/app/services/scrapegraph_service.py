from __future__ import annotations

import json
import logging
from typing import Any

import httpx
import requests

from app.config.settings import settings
from app.services.llm_service import LLMService
from app.utils.debug_log import debug_log


logger = logging.getLogger(__name__)


class ScrapeGraphService:
    def __init__(self, llm_service: LLMService) -> None:
        self.llm_service = llm_service
        self.api_key = settings.scrapegraphai_api_key
        self.base_url = (settings.scrapegraphai_base_url or "https://sgai-api-v2.onrender.com").rstrip("/")
        self.extract_endpoint = f"{self.base_url}/api/v1/extract"

    def scrape_with_schema(self, url: str, schema: dict[str, Any], instruction: str) -> dict[str, Any]:
        logger.info(
            "ScrapeGraph extract start url=%s schema_keys=%d",
            url,
            len(schema.keys()),
        )
        api_result = self._scrape_via_api(url=url, schema=schema, instruction=instruction)
        if api_result:
            logger.info("ScrapeGraph extract success via API url=%s", url)
            return self._normalize_scrape_output(api_result)

        # Fallback: fetch page content and use LLM to coerce into the target JSON schema.
        logger.warning("ScrapeGraph API failed, using fallback fetch+LLM url=%s", url)
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        content = response.text[:15000]
        prompt = (
            f"{instruction}\n"
            f"Target schema keys and types:\n{json.dumps(schema)}\n"
            "Return strict JSON only.\n"
            f"Source URL: {url}\n"
            f"Page content:\n{content}"
        )
        text = self.llm_service.json_completion(prompt)
        return self._normalize_scrape_output(json.loads(text))

    def _scrape_via_api(
        self,
        url: str,
        schema: dict[str, Any],
        instruction: str,
    ) -> dict[str, Any] | None:
        if not self.api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        prompt = f"{instruction}\nReturn JSON that matches this schema:\n{json.dumps(schema)}"
        payload = {
            "url": url,
            "prompt": prompt,
        }

        try:
            logger.info("Calling ScrapeGraph endpoint=%s url=%s", self.extract_endpoint, url)
            # region agent log
            debug_log(
                run_id="ingest-debug-1",
                hypothesis_id="H2",
                location="scrapegraph_service.py:_scrape_via_api:before_post",
                message="Calling raw ScrapeGraph extract endpoint",
                data={
                    "endpoint": self.extract_endpoint,
                    "url": url,
                    "prompt_len": len(prompt),
                    "schema_keys_count": len(schema.keys()),
                },
            )
            # endregion
            response = requests.post(
                self.extract_endpoint,
                headers=headers,
                json=payload,
                timeout=45,
            )
            logger.info(
                "ScrapeGraph response status=%s url=%s",
                response.status_code,
                url,
            )
            # region agent log
            debug_log(
                run_id="ingest-debug-1",
                hypothesis_id="H2",
                location="scrapegraph_service.py:_scrape_via_api:after_post",
                message="ScrapeGraph response received",
                data={
                    "url": url,
                    "status_code": response.status_code,
                    "ok": response.ok,
                },
            )
            # endregion
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                if isinstance(data.get("result"), dict):
                    return data["result"]
                if isinstance(data.get("data"), dict):
                    return data["data"]
                return data
        except Exception as exc:
            logger.exception("ScrapeGraph request failed url=%s error=%s", url, str(exc))
            return None
        return None

    def _normalize_scrape_output(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        # Some ScrapeGraph responses wrap extracted fields under "json".
        if isinstance(payload.get("json"), dict):
            return payload["json"]
        return payload

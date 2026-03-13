from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

from supabase import Client, create_client

from app.config.settings import settings


logger = logging.getLogger(__name__)


class SupabaseService:
    def __init__(self) -> None:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise ValueError("Supabase URL/service key not configured.")
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )

    def upsert_job(self, payload: dict[str, Any]) -> str:
        logger.info("Supabase upsert_job start source_url=%s", payload.get("source_url"))
        payload["extracted_at"] = datetime.now(timezone.utc).isoformat()
        result = (
            self.client.table("jobs")
            .upsert(payload, on_conflict="source_url")
            .execute()
        )
        row = result.data[0]
        logger.info("Supabase upsert_job success job_id=%s", row.get("id"))
        return row["id"]

    def upsert_job_embedding(self, job_id: str, embedding: list[float]) -> None:
        logger.info("Supabase upsert_job_embedding start job_id=%s dims=%d", job_id, len(embedding))
        self.client.table("job_embeddings").upsert(
            {"job_id": job_id, "embedding": embedding},
            on_conflict="job_id",
        ).execute()
        logger.info("Supabase upsert_job_embedding success job_id=%s", job_id)

    def upsert_applicant(self, payload: dict[str, Any]) -> str:
        logger.info("Supabase upsert_applicant start email=%s", payload.get("email"))
        result = (
            self.client.table("applicants")
            .upsert(payload, on_conflict="email")
            .execute()
        )
        row = result.data[0]
        logger.info("Supabase upsert_applicant success applicant_id=%s", row.get("id"))
        return row["id"]

    def upsert_applicant_embedding(self, applicant_id: str, embedding: list[float]) -> None:
        logger.info(
            "Supabase upsert_applicant_embedding start applicant_id=%s dims=%d",
            applicant_id,
            len(embedding),
        )
        self.client.table("applicant_embeddings").upsert(
            {"applicant_id": applicant_id, "embedding": embedding},
            on_conflict="applicant_id",
        ).execute()
        logger.info("Supabase upsert_applicant_embedding success applicant_id=%s", applicant_id)

    def save_fit_summary(self, payload: dict[str, Any]) -> None:
        logger.info(
            "Supabase save_fit_summary start applicant_id=%s job_id=%s",
            payload.get("applicant_id"),
            payload.get("job_id"),
        )
        self.client.table("job_applicant_matches").upsert(
            payload,
            on_conflict="applicant_id,job_id",
        ).execute()
        logger.info(
            "Supabase save_fit_summary success applicant_id=%s job_id=%s",
            payload.get("applicant_id"),
            payload.get("job_id"),
        )

    def save_generated_documents(self, rows: list[dict[str, Any]]) -> None:
        if rows:
            logger.info("Supabase save_generated_documents start count=%d", len(rows))
            self.client.table("generated_documents").insert(rows).execute()
            logger.info("Supabase save_generated_documents success count=%d", len(rows))

    def save_contacts(self, rows: list[dict[str, Any]]) -> None:
        if rows:
            logger.info("Supabase save_contacts start count=%d", len(rows))
            self.client.table("job_contacts").insert(rows).execute()
            logger.info("Supabase save_contacts success count=%d", len(rows))

    def get_job(self, job_id: str) -> dict[str, Any]:
        result = self.client.table("jobs").select("*").eq("id", job_id).limit(1).execute()
        if not result.data:
            raise ValueError("Job not found.")
        return result.data[0]

    def list_jobs(self, limit: int, offset: int, q: str | None = None) -> list[dict[str, Any]]:
        query = (
            self.client.table("jobs")
            .select(
                "id,source_url,company,title,location,job_type,description,extracted_at,requirements,responsibilities,compensation"
            )
            .order("extracted_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        if q:
            query = query.or_(f"title.ilike.%{q}%,company.ilike.%{q}%,location.ilike.%{q}%")
        result = query.execute()
        return result.data or []

    def get_applicant(self, applicant_id: str) -> dict[str, Any]:
        result = (
            self.client.table("applicants").select("*").eq("id", applicant_id).limit(1).execute()
        )
        if not result.data:
            raise ValueError("Applicant not found.")
        return result.data[0]

    def get_fit_summary(self, job_id: str, applicant_id: str) -> dict[str, Any] | None:
        result = (
            self.client.table("job_applicant_matches")
            .select("*")
            .eq("job_id", job_id)
            .eq("applicant_id", applicant_id)
            .order("updated_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_generated_documents(self, job_id: str, applicant_id: str) -> list[dict[str, Any]]:
        result = (
            self.client.table("generated_documents")
            .select("*")
            .eq("job_id", job_id)
            .eq("applicant_id", applicant_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    def get_networking_contacts(self, job_id: str) -> list[dict[str, Any]]:
        result = (
            self.client.table("job_contacts")
            .select("*")
            .eq("job_id", job_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    def search_jobs(self, query_embedding: list[float], top_k: int) -> list[dict[str, Any]]:
        logger.info("Supabase rpc search_jobs start top_k=%d dims=%d", top_k, len(query_embedding))
        result = self.client.rpc(
            "search_jobs",
            {"query_embedding": query_embedding, "top_k": top_k},
        ).execute()
        logger.info("Supabase rpc search_jobs success rows=%d", len(result.data or []))
        return result.data or []

    def search_jobs_for_applicant(
        self, query_embedding: list[float], applicant_id: str, top_k: int
    ) -> list[dict[str, Any]]:
        logger.info(
            "Supabase rpc search_jobs_for_applicant start applicant_id=%s top_k=%d dims=%d",
            applicant_id,
            top_k,
            len(query_embedding),
        )
        result = self.client.rpc(
            "search_jobs_for_applicant",
            {
                "query_embedding": query_embedding,
                "p_applicant_id": applicant_id,
                "top_k": top_k,
            },
        ).execute()
        logger.info("Supabase rpc search_jobs_for_applicant success rows=%d", len(result.data or []))
        return result.data or []

    def recommend_jobs_for_applicant(self, applicant_id: str, top_k: int) -> list[dict[str, Any]]:
        logger.info(
            "Supabase rpc recommend_jobs_for_applicant start applicant_id=%s top_k=%d",
            applicant_id,
            top_k,
        )
        result = self.client.rpc(
            "recommend_jobs_for_applicant",
            {"p_applicant_id": applicant_id, "top_k": top_k},
        ).execute()
        logger.info(
            "Supabase rpc recommend_jobs_for_applicant success rows=%d",
            len(result.data or []),
        )
        return result.data or []

from __future__ import annotations

import json
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas.applicant import ApplicantCreateRequest
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.scrapegraph_service import ScrapeGraphService
from app.services.supabase_service import SupabaseService
from app.utils.debug_log import debug_log


class JobState(TypedDict, total=False):
    url: str
    extracted: dict[str, Any]
    job_id: str


class ApplicantState(TypedDict, total=False):
    payload: dict[str, Any]
    enriched: dict[str, Any]
    applicant_id: str
    enriched_sources: list[str]


class WorkflowService:
    def __init__(
        self,
        llm_service: LLMService,
        scrape_service: ScrapeGraphService,
        embedding_service: EmbeddingService,
        supabase_service: SupabaseService,
    ) -> None:
        self.llm = llm_service
        self.scraper = scrape_service
        self.embeddings = embedding_service
        self.db = supabase_service

    def ingest_job_url(self, url: str) -> str:
        graph = StateGraph(JobState)
        graph.add_node("extract_job", self._extract_job_node)
        graph.add_node("store_job", self._store_job_node)
        graph.add_edge(START, "extract_job")
        graph.add_edge("extract_job", "store_job")
        graph.add_edge("store_job", END)
        app = graph.compile()
        result = app.invoke({"url": url})
        return result["job_id"]

    def create_or_update_applicant(self, request: ApplicantCreateRequest) -> tuple[str, list[str]]:
        graph = StateGraph(ApplicantState)
        graph.add_node("enrich_applicant", self._enrich_applicant_node)
        graph.add_node("store_applicant", self._store_applicant_node)
        graph.add_edge(START, "enrich_applicant")
        graph.add_edge("enrich_applicant", "store_applicant")
        graph.add_edge("store_applicant", END)
        app = graph.compile()
        result = app.invoke({"payload": request.model_dump(mode="json")})
        return result["applicant_id"], result.get("enriched_sources", [])

    def summarize_fit(self, applicant_id: str, job_id: str) -> dict[str, Any]:
        applicant = self.db.get_applicant(applicant_id)
        job = self.db.get_job(job_id)
        prompt = (
            "You are a career assistant. Compare this applicant with this job and return JSON with keys: "
            "score (0..1 float), requirements_summary (string), matching (list of strings), gaps (list of strings).\n"
            f"Applicant: {json.dumps(applicant)}\n"
            f"Job: {json.dumps(job)}"
        )
        parsed = json.loads(self.llm.json_completion(prompt))
        payload = {
            "applicant_id": applicant_id,
            "job_id": job_id,
            "score": parsed.get("score", 0.0),
            "requirements_summary": parsed.get("requirements_summary", ""),
            "matching_summary": "\n".join(parsed.get("matching", [])),
            "gap_summary": "\n".join(parsed.get("gaps", [])),
            "strengths_json": parsed.get("matching", []),
            "gaps_json": parsed.get("gaps", []),
        }
        self.db.save_fit_summary(payload)
        return parsed

    def generate_documents(self, applicant_id: str, job_id: str, document_type: str) -> list[dict[str, str]]:
        applicant = self.db.get_applicant(applicant_id)
        job = self.db.get_job(job_id)
        types = ["resume", "cover_letter"] if document_type == "both" else [document_type]
        rows: list[dict[str, str]] = []
        for one_type in types:
            prompt = (
                f"Generate a {one_type} in markdown based on applicant data and job data.\n"
                f"Applicant: {json.dumps(applicant)}\n"
                f"Job: {json.dumps(job)}"
            )
            content = self.llm.text_completion(prompt)
            rows.append(
                {
                    "applicant_id": applicant_id,
                    "job_id": job_id,
                    "document_type": one_type,
                    "content_markdown": content,
                }
            )
        self.db.save_generated_documents(rows)
        return [{"document_type": row["document_type"], "content_markdown": row["content_markdown"]} for row in rows]

    def generate_networking_contacts(self, applicant_id: str, job_id: str) -> list[dict[str, Any]]:
        del applicant_id
        job = self.db.get_job(job_id)
        company = job.get("company") or "the company"
        role = job.get("title") or "this role"
        query_url = f"https://www.linkedin.com/search/results/people/?keywords={company}%20{role}%20HR"
        schema = {
            "contacts": [
                {
                    "person_name": "string",
                    "role_title": "string",
                    "linkedin_url": "string",
                    "rationale": "string",
                }
            ]
        }
        extracted = self.scraper.scrape_with_schema(
            query_url,
            schema,
            "Find people likely relevant to this role (HR, hiring manager, management).",
        )
        contacts = extracted.get("contacts", [])[:10]
        rows: list[dict[str, Any]] = []
        for contact in contacts:
            person_name = contact.get("person_name", "there")
            role_title = contact.get("role_title")
            linkedin_url = contact.get("linkedin_url")
            msg_prompt = (
                "Draft a concise LinkedIn connection request message (under 300 chars). "
                f"Target person: {person_name}, role: {role_title}, company: {company}, job title: {role}."
            )
            message = self.llm.text_completion(msg_prompt)
            rows.append(
                {
                    "job_id": job_id,
                    "person_name": person_name,
                    "role_title": role_title,
                    "linkedin_url": linkedin_url,
                    "rationale": contact.get("rationale"),
                    "message": message,
                }
            )
        self.db.save_contacts(
            [
                {
                    "job_id": row["job_id"],
                    "person_name": row["person_name"],
                    "role_title": row["role_title"],
                    "linkedin_url": row["linkedin_url"],
                    "rationale": row.get("rationale"),
                    "message": row.get("message"),
                }
                for row in rows
            ]
        )
        return rows

    def _extract_job_node(self, state: JobState) -> JobState:
        schema = {
            "company": "string",
            "title": "string",
            "location": "string",
            "job_type": "string",
            "description": "string",
            "requirements": ["string"],
            "responsibilities": ["string"],
            "compensation": "string",
        }
        extracted = self.scraper.scrape_with_schema(
            state["url"],
            schema,
            "Extract job information for a job applicant platform.",
        )
        extracted["source_url"] = state["url"]
        extracted["raw_json"] = extracted.copy()
        return {"extracted": extracted}

    def _store_job_node(self, state: JobState) -> JobState:
        payload = state["extracted"]
        # region agent log
        debug_log(
            run_id="ingest-debug-1",
            hypothesis_id="H3",
            location="graphs.py:_store_job_node:before_upsert",
            message="Preparing job upsert",
            data={
                "source_url": payload.get("source_url"),
                "has_title": bool(payload.get("title")),
                "has_description": bool(payload.get("description")),
                "requirements_count": len(payload.get("requirements", [])),
            },
        )
        # endregion
        job_id = self.db.upsert_job(payload)
        emb_source = " ".join(
            [
                payload.get("title") or "",
                payload.get("company") or "",
                payload.get("location") or "",
                payload.get("description") or "",
                " ".join(payload.get("requirements", [])),
            ]
        )
        embedding = self.embeddings.embed_text(emb_source)
        self.db.upsert_job_embedding(job_id, embedding)
        # region agent log
        debug_log(
            run_id="ingest-debug-1",
            hypothesis_id="H3",
            location="graphs.py:_store_job_node:after_upsert",
            message="Job upsert and embedding succeeded",
            data={"job_id": job_id, "embedding_len": len(embedding)},
        )
        # endregion
        return {"job_id": job_id}

    def _enrich_applicant_node(self, state: ApplicantState) -> ApplicantState:
        payload = state["payload"]
        enriched = payload.copy()
        enriched_sources: list[str] = []
        target_schema = {
            "summary": "string",
            "experience": [{"company": "string", "title": "string", "details": "string"}],
            "education": [{"institution": "string", "degree": "string"}],
            "projects": [{"name": "string", "details": "string"}],
            "skills": ["string"],
        }
        for key in ("linkedin_url", "github_url", "portfolio_url", "other_url"):
            url = payload.get(key)
            if not url:
                continue
            extracted = self.scraper.scrape_with_schema(
                str(url),
                target_schema,
                "Extract applicant profile content relevant to hiring.",
            )
            enriched_sources.append(key)
            enriched["experience"] = _merge_list(enriched.get("experience", []), extracted.get("experience", []))
            enriched["education"] = _merge_list(enriched.get("education", []), extracted.get("education", []))
            enriched["projects"] = _merge_list(enriched.get("projects", []), extracted.get("projects", []))
            enriched["skills"] = _merge_skills(enriched.get("skills", []), extracted.get("skills", []))
            if not enriched.get("resume_text") and extracted.get("summary"):
                enriched["resume_text"] = extracted["summary"]
        return {"enriched": enriched, "enriched_sources": enriched_sources}

    def _store_applicant_node(self, state: ApplicantState) -> ApplicantState:
        enriched = state["enriched"]
        applicant_payload = {
            "full_name": enriched.get("full_name"),
            "email": enriched.get("email"),
            "location": enriched.get("location"),
            "phone_number": enriched.get("phone_number"),
            "linkedin_url": enriched.get("linkedin_url"),
            "github_url": enriched.get("github_url"),
            "portfolio_url": enriched.get("portfolio_url"),
            "other_url": enriched.get("other_url"),
            "resume_text": enriched.get("resume_text"),
            "experience_json": enriched.get("experience", []),
            "education_json": enriched.get("education", []),
            "projects_json": enriched.get("projects", []),
            "skills_json": enriched.get("skills", []),
            "raw_profile_json": enriched,
        }
        applicant_id = self.db.upsert_applicant(applicant_payload)
        emb_source = " ".join(
            [
                enriched.get("full_name", ""),
                enriched.get("location", ""),
                enriched.get("resume_text", "") or "",
                " ".join([str(skill) for skill in enriched.get("skills", [])]),
                json.dumps(enriched.get("experience", [])),
            ]
        )
        embedding = self.embeddings.embed_text(emb_source)
        self.db.upsert_applicant_embedding(applicant_id, embedding)
        return {
            "applicant_id": applicant_id,
            "enriched_sources": state.get("enriched_sources", []),
        }


def _merge_list(existing: list[Any], incoming: list[Any]) -> list[Any]:
    values = list(existing or [])
    for row in incoming or []:
        if row not in values:
            values.append(row)
    return values


def _merge_skills(existing: list[Any], incoming: list[Any]) -> list[str]:
    merged: list[str] = []
    for value in list(existing or []) + list(incoming or []):
        text = str(value).strip()
        if text and text not in merged:
            merged.append(text)
    return merged

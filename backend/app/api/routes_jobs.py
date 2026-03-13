from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.config.settings import settings
from app.schemas.applicant import GenerateDocumentsRequest, GeneratedDocument, NetworkingContact
from app.schemas.job import (
    FitSummaryRequest,
    FitSummaryResponse,
    IngestJobsRequest,
    IngestJobsResponse,
    JobDetailResponse,
    JobListResponseItem,
    JobSearchResponseItem,
    StoredFitSummaryResponse,
)
from app.services.container import get_workflow_service
from app.services.embedding_service import EmbeddingService
from app.services.graphs import WorkflowService
from app.services.job_urls_parser import parse_job_urls
from app.utils.debug_log import debug_log


router = APIRouter()
UUID_PATTERN = r"^[0-9a-fA-F-]{36}$"
FILE_INGEST_LIMIT = 5
logger = logging.getLogger(__name__)


@router.get("/search", response_model=list[JobSearchResponseItem])
def search_jobs(
    q: str = Query(..., min_length=2),
    top_k: int = Query(20, ge=1, le=50),
    applicant_id: str | None = Query(default=None),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> list[JobSearchResponseItem]:
    logger.info(
        "Search request received q=%s top_k=%d applicant_id=%s",
        q,
        top_k,
        applicant_id,
    )
    embedding = EmbeddingService().embed_text(q)
    if applicant_id:
        rows = workflows.db.search_jobs_for_applicant(embedding, applicant_id, top_k)
    else:
        rows = workflows.db.search_jobs(embedding, top_k)
    logger.info("Search request success rows=%d", len(rows))
    return [JobSearchResponseItem(**row) for row in rows]


@router.get("", response_model=list[JobListResponseItem])
def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: str | None = Query(default=None),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> list[JobListResponseItem]:
    rows = workflows.db.list_jobs(limit=limit, offset=offset, q=q)
    return [JobListResponseItem(**row) for row in rows]


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: str = Path(..., pattern=UUID_PATTERN),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> JobDetailResponse:
    row = workflows.db.get_job(job_id)
    return JobDetailResponse(**row)


@router.post("/ingest", response_model=IngestJobsResponse)
def ingest_jobs(
    request: IngestJobsRequest,
    workflows: WorkflowService = Depends(get_workflow_service),
) -> IngestJobsResponse:
    # region agent log
    debug_log(
        run_id="ingest-debug-1",
        hypothesis_id="H4",
        location="routes_jobs.py:ingest_jobs:start",
        message="Ingest request received",
        data={
            "read_from_file": request.read_from_file,
            "request_urls_count": len(request.urls or []),
        },
    )
    # endregion
    urls = [str(url) for url in request.urls or []]
    if request.read_from_file:
        urls.extend(parse_job_urls(settings.job_urls_file)[:FILE_INGEST_LIMIT])
    deduped = list(dict.fromkeys(urls))
    # region agent log
    debug_log(
        run_id="ingest-debug-1",
        hypothesis_id="H1",
        location="routes_jobs.py:ingest_jobs:after_parse",
        message="Parsed and deduped URLs",
        data={
            "total_after_parse": len(urls),
            "deduped_count": len(deduped),
            "sample_first_url": deduped[0] if deduped else None,
        },
    )
    # endregion
    inserted = 0
    skipped = 0
    errors: list[str] = []
    for url in deduped:
        try:
            workflows.ingest_job_url(url)
            inserted += 1
        except Exception as exc:  # pragma: no cover - integration failure path
            skipped += 1
            errors.append(f"{url}: {exc}")
            # region agent log
            debug_log(
                run_id="ingest-debug-1",
                hypothesis_id="H3",
                location="routes_jobs.py:ingest_jobs:loop_error",
                message="Per-url ingestion failed",
                data={
                    "url": url,
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:350],
                },
            )
            # endregion
    # region agent log
    debug_log(
        run_id="ingest-debug-1",
        hypothesis_id="H1",
        location="routes_jobs.py:ingest_jobs:end",
        message="Ingest completed",
        data={
            "total_urls": len(deduped),
            "inserted_or_updated": inserted,
            "skipped": skipped,
            "errors_count": len(errors),
        },
    )
    # endregion
    return IngestJobsResponse(
        total_urls=len(deduped),
        inserted_or_updated=inserted,
        skipped=skipped,
        errors=errors,
    )


@router.post("/{job_id}/fit-summary", response_model=FitSummaryResponse)
def fit_summary(
    request: FitSummaryRequest,
    job_id: str = Path(..., pattern=UUID_PATTERN),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> FitSummaryResponse:
    try:
        result = workflows.summarize_fit(applicant_id=request.applicant_id, job_id=job_id)
        return FitSummaryResponse(
            applicant_id=request.applicant_id,
            job_id=job_id,
            score=float(result.get("score", 0.0)),
            requirements_summary=result.get("requirements_summary", ""),
            matching=result.get("matching", []),
            gaps=result.get("gaps", []),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{job_id}/fit-summary", response_model=StoredFitSummaryResponse)
def get_fit_summary(
    job_id: str = Path(..., pattern=UUID_PATTERN),
    applicant_id: str = Query(...),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> StoredFitSummaryResponse:
    row = workflows.db.get_fit_summary(job_id=job_id, applicant_id=applicant_id)
    if not row:
        raise HTTPException(status_code=404, detail="Fit summary not found.")
    return StoredFitSummaryResponse(
        applicant_id=row["applicant_id"],
        job_id=row["job_id"],
        score=float(row["score"]),
        requirements_summary=row.get("requirements_summary") or "",
        matching=row.get("strengths_json") or [],
        gaps=row.get("gaps_json") or [],
    )


@router.post("/{job_id}/generate-docs", response_model=list[GeneratedDocument])
def generate_documents(
    request: GenerateDocumentsRequest,
    job_id: str = Path(..., pattern=UUID_PATTERN),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> list[GeneratedDocument]:
    rows = workflows.generate_documents(request.applicant_id, job_id, request.document_type)
    return [GeneratedDocument(**row) for row in rows]


@router.get("/{job_id}/generated-docs", response_model=list[GeneratedDocument])
def get_generated_documents(
    job_id: str = Path(..., pattern=UUID_PATTERN),
    applicant_id: str = Query(...),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> list[GeneratedDocument]:
    rows = workflows.db.get_generated_documents(job_id=job_id, applicant_id=applicant_id)
    return [GeneratedDocument(**row) for row in rows]


@router.post("/{job_id}/networking", response_model=list[NetworkingContact])
def networking_contacts(
    request: FitSummaryRequest,
    job_id: str = Path(..., pattern=UUID_PATTERN),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> list[NetworkingContact]:
    rows = workflows.generate_networking_contacts(applicant_id=request.applicant_id, job_id=job_id)
    return [
        NetworkingContact(
            person_name=row["person_name"],
            role_title=row.get("role_title"),
            linkedin_url=row.get("linkedin_url"),
            message=row["message"],
        )
        for row in rows
    ]


@router.get("/{job_id}/networking-contacts", response_model=list[NetworkingContact])
def get_networking_contacts(
    job_id: str = Path(..., pattern=UUID_PATTERN),
    workflows: WorkflowService = Depends(get_workflow_service),
) -> list[NetworkingContact]:
    rows = workflows.db.get_networking_contacts(job_id)
    return [
        NetworkingContact(
            id=row.get("id"),
            job_id=row.get("job_id"),
            person_name=row.get("person_name", ""),
            role_title=row.get("role_title"),
            linkedin_url=row.get("linkedin_url"),
            message=row.get("message") or "",
        )
        for row in rows
    ]

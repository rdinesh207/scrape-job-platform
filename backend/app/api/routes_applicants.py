from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.config.settings import settings
from app.schemas.applicant import (
    ApplicantCreateRequest,
    ApplicantCreateResponse,
    ApplicantProfileResponse,
    ApplicantRecommendationResponseItem,
)
from app.services.container import get_workflow_service
from app.services.graphs import WorkflowService


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=ApplicantCreateResponse)
def create_or_update_applicant(
    request: ApplicantCreateRequest,
    workflows: WorkflowService = Depends(get_workflow_service),
) -> ApplicantCreateResponse:
    logger.info(
        "Applicant create request received email=%s has_linkedin=%s has_github=%s has_portfolio=%s",
        request.email,
        bool(request.linkedin_url),
        bool(request.github_url),
        bool(request.portfolio_url),
    )
    applicant_id, enriched_sources = workflows.create_or_update_applicant(request)
    logger.info("Applicant create success applicant_id=%s", applicant_id)
    return ApplicantCreateResponse(
        applicant_id=applicant_id,
        enriched_sources=enriched_sources,
    )


@router.get("/{applicant_id}/recommendations", response_model=list[ApplicantRecommendationResponseItem])
def recommendations(
    applicant_id: str,
    top_k: int = settings.default_recommendation_count,
    workflows: WorkflowService = Depends(get_workflow_service),
) -> list[ApplicantRecommendationResponseItem]:
    logger.info(
        "Recommendations request received applicant_id=%s top_k=%d",
        applicant_id,
        top_k,
    )
    rows = workflows.db.recommend_jobs_for_applicant(applicant_id, top_k)
    logger.info(
        "Recommendations request success applicant_id=%s rows=%d",
        applicant_id,
        len(rows),
    )
    return [ApplicantRecommendationResponseItem(**row) for row in rows]


@router.get("/{applicant_id}", response_model=ApplicantProfileResponse)
def get_applicant_profile(
    applicant_id: str,
    workflows: WorkflowService = Depends(get_workflow_service),
) -> ApplicantProfileResponse:
    row = workflows.db.get_applicant(applicant_id)
    return ApplicantProfileResponse(**row)

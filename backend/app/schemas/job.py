from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class JobExtraction(BaseModel):
    source_url: HttpUrl
    company: str | None = None
    title: str | None = None
    location: str | None = None
    job_type: str | None = None
    description: str | None = None
    requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    compensation: str | None = None
    raw_json: dict[str, Any] = Field(default_factory=dict)


class IngestJobsRequest(BaseModel):
    urls: list[HttpUrl] | None = None
    read_from_file: bool = True


class IngestJobsResponse(BaseModel):
    total_urls: int
    inserted_or_updated: int
    skipped: int
    errors: list[str] = Field(default_factory=list)


class JobSearchResponseItem(BaseModel):
    job_id: str
    source_url: str
    company: str | None = None
    title: str | None = None
    location: str | None = None
    score: float


class JobListResponseItem(BaseModel):
    id: str
    source_url: str
    company: str | None = None
    title: str | None = None
    location: str | None = None
    job_type: str | None = None
    description: str | None = None
    extracted_at: str | None = None


class JobDetailResponse(JobListResponseItem):
    requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    compensation: str | None = None


class FitSummaryRequest(BaseModel):
    applicant_id: str


class FitSummaryResponse(BaseModel):
    applicant_id: str
    job_id: str
    score: float = Field(ge=0.0, le=1.0)
    requirements_summary: str
    matching: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class StoredFitSummaryResponse(BaseModel):
    applicant_id: str
    job_id: str
    score: float = Field(ge=0.0, le=1.0)
    requirements_summary: str
    matching: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)

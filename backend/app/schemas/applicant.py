from typing import Any

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


class ApplicantCreateRequest(BaseModel):
    full_name: str
    email: EmailStr
    location: str | None = None
    phone_number: str | None = None
    linkedin_url: HttpUrl | None = None
    github_url: HttpUrl | None = None
    portfolio_url: HttpUrl | None = None
    other_url: HttpUrl | None = None
    resume_text: str | None = None
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)

    @field_validator("linkedin_url", "github_url", "portfolio_url", "other_url", mode="before")
    @classmethod
    def empty_url_to_none(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class ApplicantCreateResponse(BaseModel):
    applicant_id: str
    enriched_sources: list[str] = Field(default_factory=list)


class ApplicantProfileResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    location: str | None = None
    phone_number: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None
    other_url: str | None = None
    resume_text: str | None = None
    experience_json: list[dict[str, Any]] = Field(default_factory=list)
    education_json: list[dict[str, Any]] = Field(default_factory=list)
    projects_json: list[dict[str, Any]] = Field(default_factory=list)
    skills_json: list[str] = Field(default_factory=list)


class ApplicantRecommendationResponseItem(BaseModel):
    job_id: str
    title: str | None = None
    company: str | None = None
    location: str | None = None
    score: float


class GenerateDocumentsRequest(BaseModel):
    applicant_id: str
    document_type: str = Field(pattern="^(resume|cover_letter|both)$")


class GeneratedDocument(BaseModel):
    id: str | None = None
    applicant_id: str | None = None
    job_id: str | None = None
    document_type: str
    content_markdown: str


class NetworkingContact(BaseModel):
    id: str | None = None
    job_id: str | None = None
    person_name: str
    role_title: str | None = None
    linkedin_url: str | None = None
    message: str

export type ApplicantPayload = {
  full_name: string;
  email: string;
  location?: string;
  phone_number?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  other_url?: string;
  resume_text?: string;
  experience: Record<string, unknown>[];
  education: Record<string, unknown>[];
  projects: Record<string, unknown>[];
  skills: string[];
};

export type ApplicantProfile = ApplicantPayload & {
  id: string;
  experience_json: Record<string, unknown>[];
  education_json: Record<string, unknown>[];
  projects_json: Record<string, unknown>[];
  skills_json: string[];
};

export type RecommendationItem = {
  job_id: string;
  title?: string;
  company?: string;
  location?: string;
  score: number;
};

export type JobItem = {
  id?: string;
  job_id?: string;
  source_url: string;
  company?: string;
  title?: string;
  location?: string;
  job_type?: string;
  description?: string;
  score?: number;
};

export type JobDetail = JobItem & {
  id: string;
  requirements: string[];
  responsibilities: string[];
  compensation?: string;
};

export type FitSummary = {
  applicant_id: string;
  job_id: string;
  score: number;
  requirements_summary: string;
  matching: string[];
  gaps: string[];
};

export type GeneratedDocument = {
  id?: string;
  applicant_id?: string;
  job_id?: string;
  document_type: "resume" | "cover_letter";
  content_markdown: string;
};

export type NetworkingContact = {
  id?: string;
  job_id?: string;
  person_name: string;
  role_title?: string;
  linkedin_url?: string;
  message: string;
};

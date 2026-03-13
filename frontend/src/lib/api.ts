import type {
  ApplicantPayload,
  ApplicantProfile,
  FitSummary,
  GeneratedDocument,
  JobDetail,
  JobItem,
  NetworkingContact,
  RecommendationItem,
} from "../types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || "/api";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  createApplicant(payload: ApplicantPayload) {
    return apiFetch<{ applicant_id: string; enriched_sources: string[] }>("/applicants", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  getApplicant(applicantId: string) {
    return apiFetch<ApplicantProfile>(`/applicants/${applicantId}`);
  },
  getRecommendations(applicantId: string, topK = 10) {
    return apiFetch<RecommendationItem[]>(
      `/applicants/${applicantId}/recommendations?top_k=${topK}`,
    );
  },
  listJobs(limit = 20, offset = 0, q?: string) {
    const query = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
    });
    if (q) query.set("q", q);
    return apiFetch<JobItem[]>(`/jobs?${query.toString()}`);
  },
  searchJobs(query: string, applicantId?: string, topK = 20) {
    const params = new URLSearchParams({
      q: query,
      top_k: String(topK),
    });
    if (applicantId) {
      params.set("applicant_id", applicantId);
    }
    return apiFetch<JobItem[]>(`/jobs/search?${params.toString()}`);
  },
  getJob(jobId: string) {
    return apiFetch<JobDetail>(`/jobs/${jobId}`);
  },
  generateFitSummary(jobId: string, applicantId: string) {
    return apiFetch<FitSummary>(`/jobs/${jobId}/fit-summary`, {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId }),
    });
  },
  getFitSummary(jobId: string, applicantId: string) {
    return apiFetch<FitSummary>(
      `/jobs/${jobId}/fit-summary?applicant_id=${encodeURIComponent(applicantId)}`,
    );
  },
  generateDocuments(jobId: string, applicantId: string, documentType: "resume" | "cover_letter" | "both") {
    return apiFetch<GeneratedDocument[]>(`/jobs/${jobId}/generate-docs`, {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId, document_type: documentType }),
    });
  },
  getGeneratedDocuments(jobId: string, applicantId: string) {
    return apiFetch<GeneratedDocument[]>(
      `/jobs/${jobId}/generated-docs?applicant_id=${encodeURIComponent(applicantId)}`,
    );
  },
  generateNetworking(jobId: string, applicantId: string) {
    return apiFetch<NetworkingContact[]>(`/jobs/${jobId}/networking`, {
      method: "POST",
      body: JSON.stringify({ applicant_id: applicantId }),
    });
  },
  getNetworking(jobId: string) {
    return apiFetch<NetworkingContact[]>(`/jobs/${jobId}/networking-contacts`);
  },
};

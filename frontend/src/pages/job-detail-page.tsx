import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "sonner";

import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { api } from "../lib/api";
import { useAuth } from "../state/auth-context";
import type { FitSummary, GeneratedDocument, JobDetail, NetworkingContact } from "../types";

export function JobDetailPage() {
  const { jobId = "" } = useParams();
  const { applicantId } = useAuth();

  const [job, setJob] = useState<JobDetail | null>(null);
  const [fitSummary, setFitSummary] = useState<FitSummary | null>(null);
  const [documents, setDocuments] = useState<GeneratedDocument[]>([]);
  const [contacts, setContacts] = useState<NetworkingContact[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!jobId) return;
    setLoading(true);
    Promise.all([api.getJob(jobId), api.getNetworking(jobId)])
      .then(([jobData, contactsData]) => {
        setJob(jobData);
        setContacts(contactsData);
      })
      .catch((error) => toast.error(String(error)))
      .finally(() => setLoading(false));
  }, [jobId]);

  useEffect(() => {
    if (!jobId || !applicantId) return;
    Promise.all([
      api.getFitSummary(jobId, applicantId).catch(() => null),
      api.getGeneratedDocuments(jobId, applicantId).catch(() => []),
    ]).then(([fit, docs]) => {
      if (fit) setFitSummary(fit);
      setDocuments(docs);
    });
  }, [jobId, applicantId]);

  const generateFit = async () => {
    if (!applicantId) {
      toast.error("Please complete your profile first.");
      return;
    }
    const result = await api.generateFitSummary(jobId, applicantId);
    setFitSummary(result);
    toast.success("Fit summary generated.");
  };

  const generateDocs = async (type: "resume" | "cover_letter" | "both") => {
    if (!applicantId) {
      toast.error("Please complete your profile first.");
      return;
    }
    const rows = await api.generateDocuments(jobId, applicantId, type);
    setDocuments(rows);
    toast.success("Document(s) generated.");
  };

  const generateContacts = async () => {
    if (!applicantId) {
      toast.error("Please complete your profile first.");
      return;
    }
    const rows = await api.generateNetworking(jobId, applicantId);
    setContacts(rows);
    toast.success("Networking contacts generated.");
  };

  if (loading) {
    return <div className="text-slate-300">Loading job details...</div>;
  }

  if (!job) {
    return <div className="text-slate-300">Job not found.</div>;
  }

  return (
    <div className="space-y-5">
      <Card>
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle>{job.title || "Untitled role"}</CardTitle>
            <CardDescription>{[job.company, job.location, job.job_type].filter(Boolean).join(" • ")}</CardDescription>
          </div>
          <a className="text-sm text-indigo-300 hover:text-indigo-200" href={job.source_url} target="_blank" rel="noreferrer">
            Open source posting
          </a>
        </div>
        <p className="mt-3 text-sm text-slate-300">{job.description}</p>
      </Card>

      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <CardTitle>Fit summary</CardTitle>
          <Button onClick={generateFit}>Generate / Refresh</Button>
        </div>
        {fitSummary ? (
          <div className="space-y-3">
            <Badge>{Math.round((fitSummary.score || 0) * 100)}% match</Badge>
            <p className="text-sm text-slate-200">{fitSummary.requirements_summary}</p>
            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <p className="mb-1 text-sm font-semibold text-slate-100">Matching</p>
                <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
                  {fitSummary.matching.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="mb-1 text-sm font-semibold text-slate-100">Gap</p>
                <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">
                  {fitSummary.gaps.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-400">No fit summary yet.</p>
        )}
      </Card>

      <Card className="space-y-3">
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => generateDocs("resume")}>Generate resume</Button>
          <Button variant="secondary" onClick={() => generateDocs("cover_letter")}>
            Generate cover letter
          </Button>
          <Button variant="ghost" onClick={() => generateDocs("both")}>
            Generate both
          </Button>
        </div>
        {documents.length === 0 ? (
          <p className="text-sm text-slate-400">No generated documents available.</p>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {documents.map((doc, index) => (
              <div key={`${doc.document_type}-${index}`} className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
                <p className="mb-2 text-sm font-semibold capitalize text-slate-200">
                  {doc.document_type.replace("_", " ")}
                </p>
                <pre className="max-h-80 overflow-auto whitespace-pre-wrap text-xs text-slate-300">
                  {doc.content_markdown}
                </pre>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card className="space-y-3">
        <div className="flex items-center justify-between">
          <CardTitle>Networking contacts</CardTitle>
          <Button variant="secondary" onClick={generateContacts}>
            Find contacts
          </Button>
        </div>
        {contacts.length === 0 ? (
          <p className="text-sm text-slate-400">No contacts yet.</p>
        ) : (
          <div className="space-y-3">
            {contacts.map((contact, index) => (
              <div key={`${contact.person_name}-${index}`} className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
                <p className="font-medium text-slate-100">{contact.person_name}</p>
                <p className="text-sm text-slate-400">{contact.role_title}</p>
                {contact.linkedin_url ? (
                  <a
                    className="text-xs text-indigo-300 hover:text-indigo-200"
                    href={contact.linkedin_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    LinkedIn profile
                  </a>
                ) : null}
                <p className="mt-2 text-sm text-slate-300">{contact.message}</p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

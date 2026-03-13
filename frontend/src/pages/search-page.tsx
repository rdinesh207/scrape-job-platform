import type { FormEvent } from "react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { api } from "../lib/api";
import { useAuth } from "../state/auth-context";
import type { JobItem } from "../types";

export function SearchPage() {
  const { applicantId } = useAuth();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState<JobItem[]>([]);

  const onSearch = async (event: FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const rows = await api.searchJobs(query, applicantId ?? undefined, 20);
      setJobs(rows);
    } catch (error) {
      toast.error(String(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <Card>
        <CardTitle>Search jobs</CardTitle>
        <CardDescription>
          Find 20 relevant jobs by keyword and show profile-aware matching scores.
        </CardDescription>
        <form className="mt-4 flex gap-2" onSubmit={onSearch}>
          <Input
            placeholder="Try: machine learning engineer, data scientist, genai product manager"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </Button>
        </form>
      </Card>

      <div className="space-y-3">
        {jobs.map((job) => {
          const id = job.job_id || job.id || "";
          return (
            <Link
              key={id}
              to={`/jobs/${id}`}
              className="block rounded-xl border border-slate-800 bg-card/70 p-4 transition hover:border-indigo-400/60"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-slate-100">{job.title || "Untitled role"}</p>
                  <p className="text-sm text-slate-400">
                    {[job.company, job.location].filter(Boolean).join(" • ")}
                  </p>
                  <p className="mt-2 line-clamp-2 text-sm text-slate-300">{job.description}</p>
                </div>
                <Badge>{Math.round((job.score || 0) * 100)}% match</Badge>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

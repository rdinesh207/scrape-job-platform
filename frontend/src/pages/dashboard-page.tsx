import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { api } from "../lib/api";
import { useAuth } from "../state/auth-context";
import type { RecommendationItem } from "../types";

export function DashboardPage() {
  const { applicantId } = useAuth();
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!applicantId) return;
    setLoading(true);
    api
      .getRecommendations(applicantId, 10)
      .then(setRecommendations)
      .catch((error) => toast.error(String(error)))
      .finally(() => setLoading(false));
  }, [applicantId]);

  return (
    <div className="space-y-5">
      <Card>
        <CardTitle>Dashboard</CardTitle>
        <CardDescription>
          Your top recommendations are generated from your profile embedding and job embeddings.
        </CardDescription>
        {!applicantId ? (
          <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
            Please complete your profile first to unlock personalized recommendations.
            <div className="mt-3">
              <Link to="/profile">
                <Button size="sm">Complete profile</Button>
              </Link>
            </div>
          </div>
        ) : null}
      </Card>

      <Card>
        <CardTitle>Top 10 recommendations</CardTitle>
        <CardDescription>Ranked by semantic similarity against your profile.</CardDescription>
        <div className="mt-4 space-y-3">
          {loading ? <p className="text-sm text-slate-400">Loading recommendations...</p> : null}
          {!loading && recommendations.length === 0 ? (
            <p className="text-sm text-slate-400">No recommendations yet.</p>
          ) : null}
          {recommendations.map((job) => (
            <Link
              key={job.job_id}
              to={`/jobs/${job.job_id}`}
              className="block rounded-lg border border-slate-800 bg-slate-900/60 p-4 transition hover:border-indigo-400/60"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-slate-100">{job.title || "Untitled role"}</p>
                  <p className="text-sm text-slate-400">
                    {[job.company, job.location].filter(Boolean).join(" • ")}
                  </p>
                </div>
                <Badge>{Math.round((job.score || 0) * 100)}% match</Badge>
              </div>
            </Link>
          ))}
        </div>
      </Card>
    </div>
  );
}

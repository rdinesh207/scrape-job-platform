import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "../components/ui/button";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { api } from "../lib/api";
import type { ApplicantPayload } from "../types";
import { useAuth } from "../state/auth-context";

function parseLines(text: string) {
  return text
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function ProfilePage() {
  const { user, applicantId, setApplicantId } = useAuth();
  const [pending, setPending] = useState(false);
  const [form, setForm] = useState<ApplicantPayload>({
    full_name: "",
    email: user?.email ?? "",
    location: "",
    phone_number: "",
    linkedin_url: "",
    github_url: "",
    portfolio_url: "",
    other_url: "",
    resume_text: "",
    experience: [],
    education: [],
    projects: [],
    skills: [],
  });
  const [experienceText, setExperienceText] = useState("");
  const [educationText, setEducationText] = useState("");
  const [projectsText, setProjectsText] = useState("");
  const [skillsText, setSkillsText] = useState("");

  useEffect(() => {
    if (!applicantId) return;
    api
      .getApplicant(applicantId)
      .then((data) => {
        setForm({
          full_name: data.full_name,
          email: data.email,
          location: data.location ?? "",
          phone_number: data.phone_number ?? "",
          linkedin_url: data.linkedin_url ?? "",
          github_url: data.github_url ?? "",
          portfolio_url: data.portfolio_url ?? "",
          other_url: data.other_url ?? "",
          resume_text: data.resume_text ?? "",
          experience: data.experience_json ?? [],
          education: data.education_json ?? [],
          projects: data.projects_json ?? [],
          skills: data.skills_json ?? [],
        });
        setExperienceText((data.experience_json ?? []).map((e) => JSON.stringify(e)).join("\n"));
        setEducationText((data.education_json ?? []).map((e) => JSON.stringify(e)).join("\n"));
        setProjectsText((data.projects_json ?? []).map((e) => JSON.stringify(e)).join("\n"));
        setSkillsText((data.skills_json ?? []).join("\n"));
      })
      .catch(() => {
        // ignore initial preload errors
      });
  }, [applicantId]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setPending(true);
    try {
      const payload: ApplicantPayload = {
        ...form,
        experience: parseLines(experienceText).map((line) => ({ detail: line })),
        education: parseLines(educationText).map((line) => ({ detail: line })),
        projects: parseLines(projectsText).map((line) => ({ detail: line })),
        skills: parseLines(skillsText),
      };
      const response = await api.createApplicant(payload);
      setApplicantId(response.applicant_id);
      toast.success("Profile saved successfully.");
    } catch (error) {
      toast.error(String(error));
    } finally {
      setPending(false);
    }
  };

  return (
    <Card className="space-y-4">
      <div>
        <CardTitle>Profile setup</CardTitle>
        <CardDescription>
          Complete your profile once, and the platform will personalize job recommendations, matching
          score, resume, and outreach messaging.
        </CardDescription>
      </div>
      <form className="grid grid-cols-1 gap-3 md:grid-cols-2" onSubmit={onSubmit}>
        <Input
          placeholder="Full name"
          value={form.full_name}
          onChange={(event) => setForm((prev) => ({ ...prev, full_name: event.target.value }))}
          required
        />
        <Input
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
          required
        />
        <Input
          placeholder="Location"
          value={form.location}
          onChange={(event) => setForm((prev) => ({ ...prev, location: event.target.value }))}
        />
        <Input
          placeholder="Phone number"
          value={form.phone_number}
          onChange={(event) => setForm((prev) => ({ ...prev, phone_number: event.target.value }))}
        />
        <Input
          placeholder="LinkedIn URL"
          value={form.linkedin_url}
          onChange={(event) => setForm((prev) => ({ ...prev, linkedin_url: event.target.value }))}
        />
        <Input
          placeholder="GitHub URL"
          value={form.github_url}
          onChange={(event) => setForm((prev) => ({ ...prev, github_url: event.target.value }))}
        />
        <Input
          placeholder="Portfolio URL"
          value={form.portfolio_url}
          onChange={(event) => setForm((prev) => ({ ...prev, portfolio_url: event.target.value }))}
        />
        <Input
          placeholder="Other URL"
          value={form.other_url}
          onChange={(event) => setForm((prev) => ({ ...prev, other_url: event.target.value }))}
        />
        <div className="md:col-span-2">
          <Textarea
            placeholder="Resume text"
            value={form.resume_text}
            onChange={(event) => setForm((prev) => ({ ...prev, resume_text: event.target.value }))}
          />
        </div>
        <div className="md:col-span-2">
          <Textarea
            placeholder="Experience (one per line)"
            value={experienceText}
            onChange={(event) => setExperienceText(event.target.value)}
          />
        </div>
        <div className="md:col-span-2">
          <Textarea
            placeholder="Education (one per line)"
            value={educationText}
            onChange={(event) => setEducationText(event.target.value)}
          />
        </div>
        <div className="md:col-span-2">
          <Textarea
            placeholder="Projects (one per line)"
            value={projectsText}
            onChange={(event) => setProjectsText(event.target.value)}
          />
        </div>
        <div className="md:col-span-2">
          <Textarea
            placeholder="Skills (one per line)"
            value={skillsText}
            onChange={(event) => setSkillsText(event.target.value)}
          />
        </div>
        <div className="md:col-span-2">
          <Button type="submit" disabled={pending}>
            {pending ? "Saving..." : "Save profile"}
          </Button>
        </div>
      </form>
    </Card>
  );
}

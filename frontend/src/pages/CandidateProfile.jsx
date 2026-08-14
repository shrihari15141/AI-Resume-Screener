import { GitCompareArrows, Star, ThumbsDown, UserCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import LoadingState from "../components/LoadingState";
import ScoreBadge from "../components/ScoreBadge";
import { api } from "../services/api";

const statuses = ["New", "Analyzed", "Shortlisted", "Under Review", "Rejected", "Interview", "Hired"];

function Section({ title, children }) {
  return (
    <section className="panel p-4 sm:p-5">
      <h2 className="text-base font-bold text-ink">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function Empty() {
  return <p className="text-sm text-slate-500">Not Found</p>;
}

export default function CandidateProfile() {
  const { id } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function load() {
    try {
      const data = await api.candidate(id);
      setCandidate(data.candidate);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, [id]);

  async function setStatus(status) {
    setSaving(true);
    try {
      const data = await api.updateCandidateStatus(id, status);
      setCandidate(data.candidate);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (error) return <p className="rounded-md bg-red-50 p-4 text-danger">{error}</p>;
  if (!candidate) return <LoadingState label="Loading candidate" />;

  const result = candidate.screening_result;
  const components = result?.component_scores || {};

  return (
    <div className="grid gap-6">
      <section className="panel p-4 sm:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold text-ink">{candidate.name}</h1>
              <ScoreBadge score={candidate.overall_score} category={candidate.match_category} />
            </div>
            <p className="mt-2 text-sm text-slate-600">{candidate.job_title}</p>
            <div className="mt-4 grid gap-2 text-sm text-slate-700 sm:grid-cols-2 lg:grid-cols-3">
              <span>Email: {candidate.email || "Not Found"}</span>
              <span>Phone: {candidate.phone || "Not Found"}</span>
              <span>Location: {candidate.location || "Not Found"}</span>
              <span>LinkedIn: {candidate.linkedin || "Not Found"}</span>
              <span>GitHub: {candidate.github || "Not Found"}</span>
              <span>Experience: {candidate.years_experience || 0} years</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="btn-primary" onClick={() => setStatus("Shortlisted")} disabled={saving}>
              <Star className="h-4 w-4" aria-hidden="true" />
              Shortlist
            </button>
            <button className="btn-secondary" onClick={() => setStatus("Under Review")} disabled={saving}>
              <UserCheck className="h-4 w-4" aria-hidden="true" />
              Review
            </button>
            <button className="btn-secondary text-danger" onClick={() => setStatus("Rejected")} disabled={saving}>
              <ThumbsDown className="h-4 w-4" aria-hidden="true" />
              Reject
            </button>
            <Link className="btn-secondary" to={`/compare?ids=${candidate.id}`}>
              <GitCompareArrows className="h-4 w-4" aria-hidden="true" />
              Compare
            </Link>
          </div>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <div className="grid gap-6">
          <Section title="AI Screening">
            <div className="grid gap-3 sm:grid-cols-2">
              {Object.entries(components).map(([key, value]) => (
                <div className="rounded-lg border border-line bg-surface p-3" key={key}>
                  <p className="text-sm font-semibold capitalize text-slate-700">{key.replaceAll("_", " ")}</p>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-white">
                    <div className="h-full rounded-full bg-brand" style={{ width: `${Math.min(100, Number(value || 0))}%` }} />
                  </div>
                  <p className="mt-2 text-sm font-bold text-ink">{Number(value || 0).toFixed(0)}%</p>
                </div>
              ))}
            </div>
          </Section>

          <Section title="AI Explanation">
            <p className="whitespace-pre-line text-sm leading-6 text-slate-700">{result?.explanation || "Not Found"}</p>
          </Section>

          <Section title="Skills Analysis">
            <div className="grid gap-4 md:grid-cols-3">
              {[
                ["Matched", result?.matched_skills || [], "bg-green-50 text-green-700"],
                ["Missing Required", result?.missing_required_skills || [], "bg-red-50 text-danger"],
                ["Missing Preferred", result?.missing_preferred_skills || [], "bg-amber-50 text-warning"]
              ].map(([label, items, classes]) => (
                <div key={label}>
                  <p className="mb-2 text-sm font-semibold text-slate-700">{label}</p>
                  <div className="flex flex-wrap gap-2">
                    {items.length ? (
                      items.map((item) => (
                        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${classes}`} key={item}>
                          {item}
                        </span>
                      ))
                    ) : (
                      <Empty />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Section>
        </div>

        <div className="grid gap-6">
          <Section title="Profile">
            <div className="grid gap-4 text-sm">
              <div>
                <p className="font-semibold text-slate-700">Skills</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {candidate.skills?.length ? candidate.skills.map((skill) => <span className="rounded-full bg-surface px-2.5 py-1 text-xs" key={skill}>{skill}</span>) : <Empty />}
                </div>
              </div>
              <div>
                <p className="font-semibold text-slate-700">Education</p>
                <div className="mt-2 grid gap-2">
                  {candidate.education?.length ? candidate.education.map((item, index) => <p key={index}>{item.degree || "Degree"} {item.year ? `- ${item.year}` : ""}</p>) : <Empty />}
                </div>
              </div>
              <div>
                <p className="font-semibold text-slate-700">Experience</p>
                <div className="mt-2 grid gap-2">
                  {candidate.experience?.length ? candidate.experience.map((item, index) => <p key={index}>{item.role || "Role"} {item.company ? `at ${item.company}` : ""}</p>) : <Empty />}
                </div>
              </div>
              <div>
                <p className="font-semibold text-slate-700">Projects</p>
                <div className="mt-2 grid gap-2">
                  {candidate.projects?.length ? candidate.projects.map((item, index) => <p key={index}>{item.name}</p>) : <Empty />}
                </div>
              </div>
              <div>
                <p className="font-semibold text-slate-700">Certifications</p>
                <div className="mt-2 grid gap-2">
                  {candidate.certifications?.length ? candidate.certifications.map((item) => <p key={item}>{item}</p>) : <Empty />}
                </div>
              </div>
            </div>
          </Section>

          <Section title="Resume Quality">
            <div className="flex items-center justify-between gap-3">
              <p className="text-3xl font-bold text-ink">{result?.ats_score || 0}/100</p>
              <select className="field max-w-44" value={candidate.status} onChange={(event) => setStatus(event.target.value)} disabled={saving}>
                {statuses.map((status) => (
                  <option key={status}>{status}</option>
                ))}
              </select>
            </div>
            <div className="mt-4 grid gap-2">
              {(result?.ats_feedback || []).slice(0, 8).map((item, index) => (
                <p className="text-sm text-slate-700" key={index}>
                  {item.label ? `${item.passed ? "OK" : "Needs work"}: ${item.label}` : JSON.stringify(item)}
                </p>
              ))}
            </div>
          </Section>
        </div>
      </div>
    </div>
  );
}

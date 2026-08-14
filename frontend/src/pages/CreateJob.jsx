import { Save, Wand2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import LoadingState from "../components/LoadingState";
import { api } from "../services/api";

const initialForm = {
  title: "",
  description: "",
  required_skills: "",
  preferred_skills: "",
  education: "",
  experience: "",
  certifications: "",
  location: "",
  employment_type: "Full-time"
};

function tags(value) {
  if (Array.isArray(value)) return value;
  return value
    .split(/[,;\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export default function CreateJob() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get("edit");
  const [form, setForm] = useState(initialForm);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(Boolean(editId));
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!editId) return;
    api
      .getJob(editId)
      .then(({ job }) => {
        setForm({
          title: job.title,
          description: job.description,
          required_skills: job.required_skills.join(", "),
          preferred_skills: job.preferred_skills.join(", "),
          education: job.education.join(", "),
          experience: `${job.experience_min || 0}${job.experience_max ? `-${job.experience_max}` : ""} years`,
          certifications: job.certifications.join(", "),
          location: job.location || "",
          employment_type: job.employment_type || "Full-time"
        });
        setAnalysis(job.analysis);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [editId]);

  const payload = useMemo(
    () => ({
      ...form,
      required_skills: tags(form.required_skills),
      preferred_skills: tags(form.preferred_skills),
      education: tags(form.education),
      certifications: tags(form.certifications)
    }),
    [form]
  );

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const data = editId ? await api.updateJob(editId, payload) : await api.createJob(payload);
      navigate(`/jobs/${data.job.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function analyze() {
    if (!form.title || !form.description) {
      setError("Add a job title and description first.");
      return;
    }
    setAnalysis({
      required_skills: payload.required_skills,
      preferred_skills: payload.preferred_skills,
      education: payload.education,
      experience: { minimum: 0, maximum: null },
      technical_keywords: [...payload.required_skills, ...payload.preferred_skills]
    });
  }

  if (loading) return <LoadingState label="Loading job" />;

  return (
    <div className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
      <section className="panel p-4 sm:p-6">
        <h1 className="text-2xl font-bold text-ink">{editId ? "Edit Job" : "Create Job"}</h1>
        <form onSubmit={submit} className="mt-6 grid gap-4">
          <div>
            <label className="label" htmlFor="title">
              Job Title
            </label>
            <input id="title" className="field mt-1" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          </div>
          <div>
            <label className="label" htmlFor="description">
              Job Description
            </label>
            <textarea
              id="description"
              className="field mt-1 min-h-44"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              required
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="required">
                Required Skills
              </label>
              <textarea id="required" className="field mt-1 min-h-24" value={form.required_skills} onChange={(e) => setForm({ ...form, required_skills: e.target.value })} />
            </div>
            <div>
              <label className="label" htmlFor="preferred">
                Preferred Skills
              </label>
              <textarea id="preferred" className="field mt-1 min-h-24" value={form.preferred_skills} onChange={(e) => setForm({ ...form, preferred_skills: e.target.value })} />
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="experience">
                Experience
              </label>
              <input id="experience" className="field mt-1" value={form.experience} onChange={(e) => setForm({ ...form, experience: e.target.value })} />
            </div>
            <div>
              <label className="label" htmlFor="education">
                Education
              </label>
              <input id="education" className="field mt-1" value={form.education} onChange={(e) => setForm({ ...form, education: e.target.value })} />
            </div>
            <div>
              <label className="label" htmlFor="certifications">
                Certifications
              </label>
              <input id="certifications" className="field mt-1" value={form.certifications} onChange={(e) => setForm({ ...form, certifications: e.target.value })} />
            </div>
            <div>
              <label className="label" htmlFor="location">
                Location
              </label>
              <input id="location" className="field mt-1" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
            </div>
            <div>
              <label className="label" htmlFor="employment">
                Employment Type
              </label>
              <select id="employment" className="field mt-1" value={form.employment_type} onChange={(e) => setForm({ ...form, employment_type: e.target.value })}>
                <option>Full-time</option>
                <option>Internship</option>
                <option>Contract</option>
                <option>Part-time</option>
                <option>Remote</option>
              </select>
            </div>
          </div>
          {error && <p className="rounded-md bg-red-50 p-3 text-sm text-danger">{error}</p>}
          <div className="flex flex-wrap gap-2">
            <button className="btn-primary" disabled={saving}>
              <Save className="h-4 w-4" aria-hidden="true" />
              {saving ? "Saving" : "Save Job"}
            </button>
            <button type="button" className="btn-secondary" onClick={analyze}>
              <Wand2 className="h-4 w-4" aria-hidden="true" />
              Analyze
            </button>
          </div>
        </form>
      </section>

      <aside className="panel h-fit p-4 sm:p-5">
        <h2 className="text-base font-semibold text-ink">Job Analysis</h2>
        {analysis ? (
          <div className="mt-4 grid gap-4 text-sm">
            {[
              ["Required", analysis.required_skills],
              ["Preferred", analysis.preferred_skills],
              ["Education", analysis.education],
              ["Keywords", analysis.technical_keywords]
            ].map(([label, items]) => (
              <div key={label}>
                <p className="mb-2 font-semibold text-slate-700">{label}</p>
                <div className="flex flex-wrap gap-2">
                  {(items || []).map((item) => (
                    <span className="rounded-full bg-surface px-2.5 py-1 text-xs font-medium text-slate-700" key={item}>
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-slate-500">No analysis yet.</p>
        )}
      </aside>
    </div>
  );
}


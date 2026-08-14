import { BrainCircuit, Download, Pencil } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import CandidateTable from "../components/CandidateTable";
import LoadingState from "../components/LoadingState";
import { api } from "../services/api";

async function downloadFile(url, filename) {
  const response = await fetch(url);
  const blob = await response.blob();
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

export default function JobDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    try {
      setData(await api.getJob(id));
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, [id]);

  async function analyze() {
    await api.analyzeJob(id);
    load();
  }

  if (error) return <p className="rounded-md bg-red-50 p-4 text-danger">{error}</p>;
  if (!data) return <LoadingState label="Loading job" />;

  const { job, candidates } = data;

  return (
    <div className="grid gap-6">
      <section className="panel p-4 sm:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-bold text-ink">{job.title}</h1>
              <span className="rounded-full bg-teal-50 px-2.5 py-1 text-xs font-semibold text-brand">{job.status}</span>
            </div>
            <p className="mt-3 max-w-4xl whitespace-pre-line text-sm leading-6 text-slate-700">{job.description}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button className="btn-secondary" onClick={analyze}>
              <BrainCircuit className="h-4 w-4" aria-hidden="true" />
              Analyze
            </button>
            <Link className="btn-secondary" to={`/jobs/create?edit=${job.id}`}>
              <Pencil className="h-4 w-4" aria-hidden="true" />
              Edit
            </Link>
            <Link className="btn-primary" to="/screening">
              Screen
            </Link>
          </div>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {[
            ["Required", job.required_skills],
            ["Preferred", job.preferred_skills],
            ["Education", job.education],
            ["Certifications", job.certifications]
          ].map(([label, items]) => (
            <div className="rounded-lg border border-line bg-surface p-3" key={label}>
              <p className="text-sm font-semibold text-slate-700">{label}</p>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {(items || []).map((item) => (
                  <span className="rounded-full bg-white px-2 py-1 text-xs text-slate-700" key={item}>
                    {item}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="panel p-4 sm:p-5">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-lg font-bold text-ink">Candidates</h2>
          <div className="flex flex-wrap gap-2">
            <button className="btn-secondary" onClick={() => downloadFile(api.exportCsvUrl(job.id), `job-${job.id}-candidates.csv`)}>
              <Download className="h-4 w-4" aria-hidden="true" />
              CSV
            </button>
            <button className="btn-secondary" onClick={() => downloadFile(api.exportJsonUrl(job.id), `job-${job.id}-candidates.json`)}>
              <Download className="h-4 w-4" aria-hidden="true" />
              JSON
            </button>
          </div>
        </div>
        <CandidateTable candidates={candidates} />
      </section>
    </div>
  );
}

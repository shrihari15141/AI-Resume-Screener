import { PlayCircle, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import CandidateTable from "../components/CandidateTable";
import LoadingState from "../components/LoadingState";
import ResumeUploader from "../components/ResumeUploader";
import { api } from "../services/api";

export default function Screening() {
  const [jobs, setJobs] = useState([]);
  const [jobId, setJobId] = useState("");
  const [files, setFiles] = useState([]);
  const [batch, setBatch] = useState(null);
  const [results, setResults] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .jobs()
      .then((data) => {
        setJobs(data.jobs);
        if (data.jobs[0]) setJobId(String(data.jobs[0].id));
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoadingJobs(false));
  }, []);

  useEffect(() => {
    if (!batch?.batch_id || batch.status === "complete" || batch.status === "failed") return;
    const timer = window.setInterval(async () => {
      const status = await api.batchStatus(batch.batch_id);
      setBatch(status);
      if (status.status === "complete") {
        const data = await api.batchResults(batch.batch_id);
        setResults(data.candidates);
      }
    }, 1500);
    return () => window.clearInterval(timer);
  }, [batch?.batch_id, batch?.status]);

  const fileCount = useMemo(() => files.length, [files]);
  const progress = batch?.total ? Math.round((batch.processed / batch.total) * 100) : 0;

  async function start() {
    if (!jobId || !fileCount) {
      setError("Select a job and resumes.");
      return;
    }
    setError("");
    setSubmitting(true);
    setResults([]);
    try {
      const formData = new FormData();
      formData.append("job_id", jobId);
      files.forEach((file) => formData.append("resumes", file));
      const response = await api.uploadResumes(formData);
      setBatch(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function refresh() {
    if (!batch?.batch_id) return;
    const status = await api.batchStatus(batch.batch_id);
    setBatch(status);
    if (status.status === "complete") {
      const data = await api.batchResults(batch.batch_id);
      setResults(data.candidates);
    }
  }

  if (loadingJobs) return <LoadingState label="Loading jobs" />;

  return (
    <div className="grid gap-6">
      <div>
        <h1 className="text-2xl font-bold text-ink">AI Screening</h1>
        <p className="mt-1 text-sm text-slate-600">Upload batch resumes and rank candidates for a selected job.</p>
      </div>

      <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="panel h-fit p-4 sm:p-5">
          <label className="label" htmlFor="job">
            Select Job
          </label>
          <select id="job" className="field mt-1" value={jobId} onChange={(event) => setJobId(event.target.value)}>
            {jobs.map((job) => (
              <option value={job.id} key={job.id}>
                {job.title}
              </option>
            ))}
          </select>
          <div className="mt-5 flex flex-wrap gap-2">
            <button className="btn-primary" onClick={start} disabled={submitting || !jobId || !fileCount}>
              <PlayCircle className="h-4 w-4" aria-hidden="true" />
              {submitting ? "Submitting" : "Start AI Analysis"}
            </button>
            <button className="btn-secondary" onClick={refresh} disabled={!batch?.batch_id}>
              <RefreshCw className="h-4 w-4" aria-hidden="true" />
              Refresh
            </button>
          </div>
          {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm text-danger">{error}</p>}
        </div>
        <ResumeUploader files={files} setFiles={setFiles} />
      </section>

      {batch && (
        <section className="panel p-4 sm:p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-bold text-ink">Batch Progress</h2>
              <p className="mt-1 text-sm text-slate-600">{batch.stage || batch.status}</p>
            </div>
            <span className="rounded-full bg-teal-50 px-3 py-1 text-sm font-semibold text-brand">{batch.status}</span>
          </div>
          <div className="mt-4 h-3 overflow-hidden rounded-full bg-surface">
            <div className="h-full rounded-full bg-brand transition-all" style={{ width: `${progress}%` }} />
          </div>
          <div className="mt-3 grid gap-2 text-sm text-slate-700 sm:grid-cols-4">
            <span>Processing {batch.processed || 0} / {batch.total || 0}</span>
            <span>{batch.success || 0} processed</span>
            <span>{batch.failed || 0} failed</span>
            <span>{batch.duplicates || 0} possible duplicates</span>
          </div>
          <div className="mt-4 max-h-72 overflow-y-auto rounded-lg border border-line">
            {(batch.files || []).map((file, index) => (
              <div className="flex items-center justify-between gap-3 border-b border-line px-3 py-2 last:border-b-0" key={`${file.filename}-${index}`}>
                <span className="truncate text-sm text-ink">{file.filename}</span>
                <span className={`shrink-0 text-xs font-semibold ${file.status === "failed" || file.status === "rejected" ? "text-danger" : "text-brand"}`}>{file.status}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {results.length > 0 && (
        <section className="panel p-4 sm:p-5">
          <h2 className="mb-4 text-lg font-bold text-ink">Ranked Results</h2>
          <CandidateTable candidates={results} />
        </section>
      )}
    </div>
  );
}

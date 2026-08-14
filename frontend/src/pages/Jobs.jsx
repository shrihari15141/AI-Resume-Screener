import { Archive, Edit, Plus, Trash2, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import LoadingState from "../components/LoadingState";
import { api } from "../services/api";

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadJobs() {
    setLoading(true);
    try {
      const data = await api.jobs();
      setJobs(data.jobs);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadJobs();
  }, []);

  async function closeJob(id) {
    await api.closeJob(id);
    loadJobs();
  }

  async function deleteJob(id) {
    if (!window.confirm("Delete this job and its candidates?")) return;
    await api.deleteJob(id);
    loadJobs();
  }

  if (loading) return <LoadingState label="Loading jobs" />;

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">Jobs</h1>
          <p className="mt-1 text-sm text-slate-600">{jobs.length} openings</p>
        </div>
        <Link className="btn-primary" to="/jobs/create">
          <Plus className="h-4 w-4" aria-hidden="true" />
          Create Job
        </Link>
      </div>
      {error && <p className="rounded-md bg-red-50 p-4 text-danger">{error}</p>}

      {jobs.length === 0 ? (
        <div className="panel p-8 text-center">
          <p className="font-semibold text-ink">No jobs yet</p>
          <Link className="btn-primary mt-4" to="/jobs/create">
            <Plus className="h-4 w-4" aria-hidden="true" />
            Create Job
          </Link>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {jobs.map((job) => (
            <article className="panel flex flex-col p-5" key={job.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-bold text-ink">{job.title}</h2>
                  <p className="mt-1 text-sm text-slate-500">Created: {new Date(job.created_at).toLocaleDateString()}</p>
                </div>
                <span className="rounded-full bg-teal-50 px-2.5 py-1 text-xs font-semibold text-brand">{job.status}</span>
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-md bg-surface p-3">
                  <p className="font-semibold text-ink">{job.candidate_count}</p>
                  <p className="text-slate-500">Candidates</p>
                </div>
                <div className="rounded-md bg-surface p-3">
                  <p className="font-semibold text-ink">{job.shortlisted_count}</p>
                  <p className="text-slate-500">Shortlisted</p>
                </div>
                <div className="rounded-md bg-surface p-3">
                  <p className="font-semibold text-ink">{job.under_review_count}</p>
                  <p className="text-slate-500">Review</p>
                </div>
                <div className="rounded-md bg-surface p-3">
                  <p className="font-semibold text-ink">{job.rejected_count}</p>
                  <p className="text-slate-500">Rejected</p>
                </div>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <Link className="btn-primary" to={`/jobs/${job.id}`}>
                  <Users className="h-4 w-4" aria-hidden="true" />
                  View
                </Link>
                <Link className="btn-secondary" to={`/jobs/create?edit=${job.id}`}>
                  <Edit className="h-4 w-4" aria-hidden="true" />
                  Edit
                </Link>
                <button className="btn-secondary" onClick={() => closeJob(job.id)}>
                  <Archive className="h-4 w-4" aria-hidden="true" />
                  Close
                </button>
                <button className="btn-secondary text-danger" onClick={() => deleteJob(job.id)}>
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}


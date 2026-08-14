import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import CandidateTable from "../components/CandidateTable";
import LoadingState from "../components/LoadingState";
import StatCard from "../components/StatCard";
import { api } from "../services/api";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .reports()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="rounded-md bg-red-50 p-4 text-danger">{error}</p>;
  if (!data) return <LoadingState label="Loading dashboard" />;

  const distribution = Object.entries(data.distribution).map(([range, count]) => ({ range, count }));
  const summary = data.summary;

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-600">AI screening is decision support and recruiters should review candidates before final hiring decisions.</p>
        </div>
        <Link className="btn-primary" to="/screening">
          Start Screening
        </Link>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Active Jobs" value={summary.active_jobs} />
        <StatCard label="Total Resumes" value={summary.total_resumes} tone="accent" />
        <StatCard label="Shortlisted" value={summary.shortlisted} />
        <StatCard label="Average Score" value={`${summary.average_match_score}%`} tone="warning" />
        <StatCard label="Total Candidates" value={summary.total_candidates} tone="accent" />
        <StatCard label="Under Review" value={summary.under_review} tone="warning" />
        <StatCard label="Rejected" value={summary.rejected} tone="danger" />
      </section>

      <section className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
        <div className="panel p-4 sm:p-5">
          <h2 className="text-base font-semibold text-ink">Score Distribution</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d8dee8" />
                <XAxis dataKey="range" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#0f766e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel p-4 sm:p-5">
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="text-base font-semibold text-ink">Recent Candidates</h2>
            <Link className="text-sm font-semibold text-brand" to="/candidates">
              View all
            </Link>
          </div>
          <CandidateTable candidates={data.recent_candidates} />
        </div>
      </section>
    </div>
  );
}


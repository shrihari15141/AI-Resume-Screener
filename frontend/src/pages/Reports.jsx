import { Download } from "lucide-react";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
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

export default function Reports() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .reports()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="rounded-md bg-red-50 p-4 text-danger">{error}</p>;
  if (!data) return <LoadingState label="Loading reports" />;

  const distribution = Object.entries(data.distribution).map(([range, count]) => ({ range, count }));

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">Reports</h1>
          <p className="mt-1 text-sm text-slate-600">Candidate distribution, skills, gaps, and job statistics.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="btn-secondary" onClick={() => downloadFile(api.exportCsvUrl(), "resume-screening-results.csv")}>
            <Download className="h-4 w-4" aria-hidden="true" />
            CSV
          </button>
          <button className="btn-secondary" onClick={() => downloadFile(api.exportJsonUrl(), "resume-screening-results.json")}>
            <Download className="h-4 w-4" aria-hidden="true" />
            JSON
          </button>
        </div>
      </div>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="panel p-4 sm:p-5">
          <h2 className="text-base font-bold text-ink">Candidate Distribution</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d8dee8" />
                <XAxis dataKey="range" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="panel p-4 sm:p-5">
          <h2 className="text-base font-bold text-ink">Job Statistics</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.job_stats}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d8dee8" />
                <XAxis dataKey="job" hide />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="candidates" fill="#0f766e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="shortlisted" fill="#2563eb" radius={[4, 4, 0, 0]} />
                <Bar dataKey="rejected" fill="#dc2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="panel p-4 sm:p-5">
          <h2 className="text-base font-bold text-ink">Common Skills</h2>
          <div className="mt-4 grid gap-2">
            {data.common_skills.map((item) => (
              <div className="flex items-center justify-between rounded-md bg-surface px-3 py-2" key={item.skill}>
                <span className="text-sm font-medium text-ink">{item.skill}</span>
                <span className="text-sm text-slate-600">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="panel p-4 sm:p-5">
          <h2 className="text-base font-bold text-ink">Missing Skills</h2>
          <div className="mt-4 grid gap-2">
            {data.missing_skills.map((item) => (
              <div className="flex items-center justify-between rounded-md bg-surface px-3 py-2" key={item.skill}>
                <span className="text-sm font-medium text-ink">{item.skill}</span>
                <span className="text-sm text-slate-600">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

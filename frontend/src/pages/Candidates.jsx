import { GitCompareArrows, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import CandidateTable from "../components/CandidateTable";
import LoadingState from "../components/LoadingState";
import { api } from "../services/api";

export default function Candidates({ shortlistedOnly = false }) {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [filters, setFilters] = useState({ search: "", status: shortlistedOnly ? "Shortlisted" : "", sort: "score" });
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    try {
      const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value));
      const data = await api.candidates(params);
      setCandidates(data.candidates);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [filters.status, filters.sort, shortlistedOnly]);

  function toggle(id) {
    setSelected((current) => (current.includes(id) ? current.filter((item) => item !== id) : current.length < 5 ? [...current, id] : current));
  }

  function compare() {
    if (selected.length < 2) return;
    navigate(`/compare?ids=${selected.join(",")}`);
  }

  if (loading) return <LoadingState label="Loading candidates" />;

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">{shortlistedOnly ? "Shortlisted" : "Candidates"}</h1>
          <p className="mt-1 text-sm text-slate-600">{candidates.length} records</p>
        </div>
        <button className="btn-primary" onClick={compare} disabled={selected.length < 2}>
          <GitCompareArrows className="h-4 w-4" aria-hidden="true" />
          Compare
        </button>
      </div>
      {error && <p className="rounded-md bg-red-50 p-4 text-danger">{error}</p>}
      <section className="panel p-4">
        <div className="grid gap-3 md:grid-cols-[1fr_180px_180px_auto]">
          <label className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
            <input
              className="field pl-9"
              value={filters.search}
              onChange={(event) => setFilters({ ...filters, search: event.target.value })}
              onKeyDown={(event) => event.key === "Enter" && load()}
              placeholder="Search"
            />
          </label>
          <select className="field" value={filters.status} onChange={(event) => setFilters({ ...filters, status: event.target.value })} disabled={shortlistedOnly}>
            <option value="">All Statuses</option>
            {["New", "Analyzed", "Shortlisted", "Under Review", "Rejected", "Interview", "Hired"].map((status) => (
              <option key={status}>{status}</option>
            ))}
          </select>
          <select className="field" value={filters.sort} onChange={(event) => setFilters({ ...filters, sort: event.target.value })}>
            <option value="score">Score</option>
            <option value="name">Name</option>
            <option value="experience">Experience</option>
            <option value="status">Status</option>
          </select>
          <button className="btn-secondary" onClick={load}>
            Search
          </button>
        </div>
      </section>
      <CandidateTable candidates={candidates} selectable selected={selected} onSelect={toggle} />
    </div>
  );
}


import { GitCompareArrows } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import CandidateTable from "../components/CandidateTable";
import LoadingState from "../components/LoadingState";
import ScoreBadge from "../components/ScoreBadge";
import { api } from "../services/api";

export default function Compare() {
  const [searchParams] = useSearchParams();
  const initialIds = useMemo(() => searchParams.get("ids")?.split(",").map(Number).filter(Boolean) || [], [searchParams]);
  const [candidates, setCandidates] = useState([]);
  const [selected, setSelected] = useState(initialIds);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .candidates()
      .then((data) => setCandidates(data.candidates))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (initialIds.length >= 2) runCompare(initialIds);
  }, [initialIds.join(",")]);

  function toggle(id) {
    setSelected((current) => (current.includes(id) ? current.filter((item) => item !== id) : current.length < 5 ? [...current, id] : current));
  }

  async function runCompare(ids = selected) {
    if (ids.length < 2) return;
    try {
      const data = await api.compareCandidates(ids);
      setComparison(data);
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <LoadingState label="Loading comparison" />;

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">Compare Candidates</h1>
          <p className="mt-1 text-sm text-slate-600">Select 2 to 5 candidates.</p>
        </div>
        <button className="btn-primary" onClick={() => runCompare()} disabled={selected.length < 2}>
          <GitCompareArrows className="h-4 w-4" aria-hidden="true" />
          Compare
        </button>
      </div>
      {error && <p className="rounded-md bg-red-50 p-4 text-danger">{error}</p>}

      <CandidateTable candidates={candidates} selectable selected={selected} onSelect={toggle} />

      {comparison && (
        <section className="panel overflow-hidden p-4 sm:p-5">
          <h2 className="text-lg font-bold text-ink">Comparison Matrix</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-[760px] divide-y divide-line">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-sm font-semibold text-slate-700">Criteria</th>
                  {comparison.comparison.map((item) => (
                    <th className="px-3 py-3 text-left text-sm font-semibold text-slate-700" key={item.candidate.id}>
                      {item.candidate.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                <tr>
                  <td className="px-3 py-3 text-sm font-semibold text-slate-700">Overall</td>
                  {comparison.comparison.map((item) => (
                    <td className="px-3 py-3" key={item.candidate.id}>
                      <ScoreBadge score={item.candidate.overall_score} category={item.candidate.match_category} />
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="px-3 py-3 text-sm font-semibold text-slate-700">Experience</td>
                  {comparison.comparison.map((item) => (
                    <td className="px-3 py-3 text-sm text-slate-700" key={item.candidate.id}>
                      {item.candidate.years_experience || 0} years
                    </td>
                  ))}
                </tr>
                {comparison.skills.map((skill) => (
                  <tr key={skill}>
                    <td className="px-3 py-3 text-sm font-semibold text-slate-700">{skill}</td>
                    {comparison.comparison.map((item) => (
                      <td className={item.skills[skill] ? "px-3 py-3 text-sm font-bold text-brand" : "px-3 py-3 text-sm font-bold text-danger"} key={item.candidate.id}>
                        {item.skills[skill] ? "Matched" : "Missing"}
                      </td>
                    ))}
                  </tr>
                ))}
                <tr>
                  <td className="px-3 py-3 text-sm font-semibold text-slate-700">Recommendation</td>
                  {comparison.comparison.map((item) => (
                    <td className="px-3 py-3 text-sm font-semibold text-ink" key={item.candidate.id}>
                      {item.candidate.recommendation}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}


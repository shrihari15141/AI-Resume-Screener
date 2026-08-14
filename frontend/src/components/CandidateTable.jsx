import { Link } from "react-router-dom";
import ScoreBadge from "./ScoreBadge";

export default function CandidateTable({ candidates = [], selectable = false, selected = [], onSelect }) {
  const isSelected = (id) => selected.includes(id);

  return (
    <div>
      <div className="hidden overflow-hidden rounded-lg border border-line bg-white lg:block">
        <table className="min-w-full divide-y divide-line">
          <thead className="bg-surface">
            <tr>
              {selectable && <th className="w-12 px-4 py-3 text-left" />}
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">Candidate</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">Job</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">Score</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">Experience</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-500">Status</th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase text-slate-500">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {candidates.map((candidate) => (
              <tr key={candidate.id}>
                {selectable && (
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={isSelected(candidate.id)}
                      onChange={() => onSelect(candidate.id)}
                      className="h-4 w-4 rounded border-line text-brand focus:ring-brand"
                    />
                  </td>
                )}
                <td className="px-4 py-3">
                  <div className="font-semibold text-ink">{candidate.name}</div>
                  <div className="text-sm text-slate-500">{candidate.email || "No email"}</div>
                </td>
                <td className="px-4 py-3 text-sm text-slate-700">{candidate.job_title}</td>
                <td className="px-4 py-3">
                  <ScoreBadge score={candidate.overall_score} category={candidate.match_category} />
                </td>
                <td className="px-4 py-3 text-sm text-slate-700">{candidate.years_experience || 0} yrs</td>
                <td className="px-4 py-3 text-sm text-slate-700">{candidate.status}</td>
                <td className="px-4 py-3 text-right">
                  <Link className="text-sm font-semibold text-brand hover:text-teal-800" to={`/candidates/${candidate.id}`}>
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid gap-3 lg:hidden">
        {candidates.map((candidate) => (
          <div className="panel p-4" key={candidate.id}>
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate font-semibold text-ink">{candidate.name}</p>
                <p className="truncate text-sm text-slate-500">{candidate.email || candidate.phone || "Contact not found"}</p>
              </div>
              {selectable && (
                <input
                  type="checkbox"
                  checked={isSelected(candidate.id)}
                  onChange={() => onSelect(candidate.id)}
                  className="mt-1 h-4 w-4 rounded border-line text-brand focus:ring-brand"
                />
              )}
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <ScoreBadge score={candidate.overall_score} category={candidate.match_category} />
              <span className="rounded-full bg-surface px-2.5 py-1 text-xs font-medium text-slate-700">{candidate.status}</span>
            </div>
            <div className="mt-3 flex items-center justify-between gap-2 text-sm text-slate-600">
              <span className="truncate">{candidate.job_title}</span>
              <Link className="font-semibold text-brand" to={`/candidates/${candidate.id}`}>
                View
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


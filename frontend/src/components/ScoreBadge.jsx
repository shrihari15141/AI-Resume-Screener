export default function ScoreBadge({ score, category }) {
  const value = Number(score ?? 0);
  let classes = "bg-red-50 text-danger border-red-200";
  if (value >= 90) classes = "bg-green-50 text-green-700 border-green-200";
  else if (value >= 80) classes = "bg-emerald-50 text-emerald-700 border-emerald-200";
  else if (value >= 70) classes = "bg-blue-50 text-accent border-blue-200";
  else if (value >= 60) classes = "bg-amber-50 text-warning border-amber-200";

  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold ${classes}`}>
      {value.toFixed(0)}%
      {category ? <span className="hidden sm:inline"> {category}</span> : null}
    </span>
  );
}


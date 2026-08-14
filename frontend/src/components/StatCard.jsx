export default function StatCard({ label, value, tone = "brand" }) {
  const tones = {
    brand: "border-teal-200 bg-teal-50 text-brand",
    accent: "border-blue-200 bg-blue-50 text-accent",
    warning: "border-amber-200 bg-amber-50 text-warning",
    danger: "border-red-200 bg-red-50 text-danger"
  };

  return (
    <div className="panel p-4">
      <div className={`mb-3 h-2 w-12 rounded-full border ${tones[tone] || tones.brand}`} />
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-bold text-ink">{value}</p>
    </div>
  );
}


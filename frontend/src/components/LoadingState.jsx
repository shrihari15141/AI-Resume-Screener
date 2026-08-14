export default function LoadingState({ label = "Loading" }) {
  return (
    <div className="panel flex items-center gap-3 p-4 text-sm text-slate-600">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-brand border-r-transparent" />
      {label}
    </div>
  );
}


import { ShieldCheck } from "lucide-react";

export default function Profile() {
  return (
    <div className="grid gap-6">
      <section className="panel p-4 sm:p-6">
        <h1 className="text-2xl font-bold text-ink">Workspace</h1>
        <div className="mt-5 grid gap-3 text-sm text-slate-700">
          <p>Name: Demo Recruiter</p>
          <p>Access: No login required</p>
        </div>
      </section>
      <section className="panel p-4 sm:p-6">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-0.5 h-5 w-5 text-brand" aria-hidden="true" />
          <div>
            <h2 className="font-bold text-ink">Fairness Notice</h2>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              AI screening is decision support and should not be used as the sole basis for employment decisions. Protected characteristics are not used for scoring.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

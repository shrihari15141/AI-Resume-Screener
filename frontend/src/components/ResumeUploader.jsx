import { UploadCloud } from "lucide-react";
import { useMemo } from "react";

function formatSize(bytes) {
  if (!bytes) return "0 KB";
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ResumeUploader({ files, setFiles }) {
  const fileList = useMemo(() => Array.from(files || []), [files]);

  function addFiles(selectedFiles) {
    const incoming = Array.from(selectedFiles || []);
    setFiles((current = []) => {
      const existing = Array.from(current || []);
      const bySignature = new Map(
        existing.map((file) => [`${file.name}-${file.size}-${file.lastModified}`, file])
      );
      incoming.forEach((file) => {
        bySignature.set(`${file.name}-${file.size}-${file.lastModified}`, file);
      });
      return Array.from(bySignature.values());
    });
  }

  function removeFile(fileToRemove) {
    setFiles((current = []) =>
      Array.from(current || []).filter(
        (file) =>
          `${file.name}-${file.size}-${file.lastModified}` !==
          `${fileToRemove.name}-${fileToRemove.size}-${fileToRemove.lastModified}`
      )
    );
  }

  return (
    <div className="panel p-4 sm:p-6">
      <label className="flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-line bg-surface px-4 py-8 text-center hover:border-brand hover:bg-teal-50">
        <UploadCloud className="mb-3 h-9 w-9 text-brand" aria-hidden="true" />
        <span className="text-base font-semibold text-ink">Upload resumes</span>
        <span className="mt-1 text-sm text-slate-500">PDF, DOCX, or TXT</span>
        <input
          className="sr-only"
          type="file"
          multiple
          accept=".pdf,.docx,.txt"
          onChange={(event) => {
            addFiles(event.target.files);
            event.target.value = "";
          }}
        />
      </label>

      <div className="mt-4">
        <p className="text-sm font-semibold text-ink">{fileList.length} files selected</p>
        {fileList.length > 0 && (
          <div className="mt-3 max-h-64 overflow-y-auto rounded-lg border border-line">
            {fileList.map((file) => (
              <div key={`${file.name}-${file.size}`} className="flex items-center justify-between gap-3 border-b border-line px-3 py-2 last:border-b-0">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-ink">{file.name}</p>
                  <p className="text-xs text-slate-500">{file.type || file.name.split(".").pop()?.toUpperCase()}</p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <span className="text-xs text-slate-500">{formatSize(file.size)}</span>
                  <button
                    type="button"
                    className="text-xs font-semibold text-danger hover:text-red-800"
                    onClick={() => removeFile(file)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

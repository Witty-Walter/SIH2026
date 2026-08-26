export function RiskBadge({ status }: { status: string }) {
  if (!status) return null;
  
  let bg = "bg-slate-700", text = "text-slate-300", icon = "ℹ️";
  if (status === "SAFE") { bg = "bg-green-900/50"; text = "text-green-400"; icon = "🟢"; }
  if (status === "CAUTION") { bg = "bg-yellow-900/50"; text = "text-yellow-400"; icon = "🟡"; }
  if (status === "UNSAFE") { bg = "bg-red-900/50"; text = "text-red-400"; icon = "🔴"; }
  
  return (
    <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium border border-current ${bg} ${text}`}>
      <span>{icon}</span>
      <span>{status}</span>
    </span>
  );
}

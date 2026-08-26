import { RiskBadge } from "./RiskBadge";

export function MessageBubble({ role, text, status }: { role: "user" | "assistant", text: string, status?: string }) {
  const isUser = role === "user";
  
  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
        isUser 
          ? "bg-blue-600 text-white rounded-tr-sm" 
          : "bg-slate-800 border border-slate-700 text-slate-200 rounded-tl-sm shadow-md"
      }`}>
        {!isUser && status && (
          <div className="mb-2 border-b border-slate-700 pb-2">
            <RiskBadge status={status} />
          </div>
        )}
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {text}
        </div>
      </div>
    </div>
  );
}

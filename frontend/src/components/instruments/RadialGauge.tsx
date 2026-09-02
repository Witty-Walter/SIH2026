export function RadialGauge({ value, label, status }: { value: number, label: string, status: string }) {
  const radius = 24;
  const circumference = 2 * Math.PI * radius;
  // Cap value between 0 and 100 for safety
  const safeValue = Math.min(Math.max(value, 0), 100);
  const strokeDashoffset = circumference - (safeValue / 100) * circumference;
  
  let color = "text-marine-safe";
  if (status === "CAUTION") color = "text-marine-caution";
  if (status === "UNSAFE") color = "text-marine-danger";

  return (
    <div className="flex flex-col items-center justify-center p-2 bg-marine-navy/30 rounded-xl border border-marine-teal/20">
      <div className="relative w-14 h-14 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 64 64">
          <circle 
            className="text-marine-navy stroke-current" 
            strokeWidth="6" 
            cx="32" cy="32" r="24" fill="transparent" 
          />
          <circle 
            className={`${color} stroke-current transition-all duration-1000 ease-out`} 
            strokeWidth="6" 
            strokeLinecap="round"
            cx="32" cy="32" r="24" fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
          />
        </svg>
        <span className="absolute text-sm font-bold text-marine-offwhite">{safeValue}</span>
      </div>
      <span className="text-[9px] text-marine-offwhite/60 uppercase tracking-widest mt-2 font-semibold">{label}</span>
    </div>
  );
}

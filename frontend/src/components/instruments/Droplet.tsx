export function Droplet({ intensity, label }: { intensity: number, label: string }) {
  // intensity 0 to 100
  const safeIntensity = Math.min(Math.max(intensity, 0), 100);
  
  let fillClass = "fill-marine-teal/20";
  let activeClass = "fill-marine-safe";
  
  if (safeIntensity > 50) activeClass = "fill-marine-caution";
  if (safeIntensity > 80) activeClass = "fill-marine-danger";

  // Calculate clip path height based on intensity
  // When intensity is 100, Y is 0. When intensity is 0, Y is 100.
  const clipY = 100 - safeIntensity;

  return (
    <div className="flex flex-col items-center justify-center p-2 bg-marine-navy/30 rounded-xl border border-marine-teal/20">
      <div className="relative w-14 h-14 flex items-center justify-center">
        
        {/* Background droplet (empty) */}
        <svg viewBox="0 0 100 100" className={`w-10 h-10 ${fillClass} stroke-marine-teal stroke-2`}>
          <path d="M50 5 C50 5 20 45 20 65 C20 81.568 33.431 95 50 95 C66.568 95 80 81.568 80 65 C80 45 50 5 50 5 Z" />
        </svg>

        {/* Foreground droplet (filled) - clipped */}
        <svg viewBox="0 0 100 100" className={`absolute w-10 h-10 ${activeClass} transition-all duration-1000`}>
          <defs>
            <clipPath id="waterFill">
              <rect x="0" y={clipY} width="100" height="100" />
            </clipPath>
          </defs>
          <path clipPath="url(#waterFill)" d="M50 5 C50 5 20 45 20 65 C20 81.568 33.431 95 50 95 C66.568 95 80 81.568 80 65 C80 45 50 5 50 5 Z" />
        </svg>

      </div>
      <div className="mt-2 text-xs font-mono text-marine-offwhite">{safeIntensity}%</div>
      <span className="text-[9px] text-marine-offwhite/60 uppercase tracking-widest font-semibold">{label}</span>
    </div>
  );
}

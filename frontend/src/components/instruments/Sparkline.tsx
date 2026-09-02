export function Sparkline({ data, label, unit }: { data: number[], label: string, unit: string }) {
  const max = Math.max(...data, 1);
  const min = Math.min(...data, 0);
  const range = max - min;
  
  // Create an SVG path from the data points
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - (((val - min) / range) * 80 + 10); // scale y to 10-90
    return `${x},${y}`;
  }).join(" ");

  return (
    <div className="flex flex-col items-center justify-center p-2 bg-marine-navy/30 rounded-xl border border-marine-teal/20 w-24">
      <div className="w-full h-10 flex items-center justify-center">
         <svg className="w-full h-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
           <polyline 
             points={points} 
             fill="none" 
             className="stroke-marine-teal" 
             strokeWidth="4" 
             strokeLinecap="round" 
             strokeLinejoin="round"
           />
           {/* Current value dot at the end */}
           <circle 
              cx="100" 
              cy={100 - (((data[data.length - 1] - min) / range) * 80 + 10)} 
              r="6" 
              className="fill-marine-safe" 
            />
         </svg>
      </div>
      <div className="mt-2 flex items-baseline space-x-1">
        <span className="text-xs font-mono font-bold text-marine-offwhite">{data[data.length - 1]?.toFixed(1)}</span>
        <span className="text-[10px] font-mono text-marine-offwhite/60">{unit}</span>
      </div>
      <span className="text-[9px] text-marine-offwhite/60 uppercase tracking-widest font-semibold">{label}</span>
    </div>
  );
}

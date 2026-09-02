export function CompassNeedle({ direction, speed, label }: { direction: number, speed: number, label: string }) {
  // direction is degrees from North (0 is North, 90 is East, etc)
  return (
    <div className="flex flex-col items-center justify-center p-2 bg-marine-navy/30 rounded-xl border border-marine-teal/20">
      <div className="relative w-14 h-14 flex items-center justify-center rounded-full bg-marine-navy/50 border-2 border-marine-teal/30">
        {/* Compass rose markings */}
        <div className="absolute top-1 text-[8px] text-marine-offwhite/40 font-bold">N</div>
        <div className="absolute bottom-1 text-[8px] text-marine-offwhite/40 font-bold">S</div>
        <div className="absolute right-1 text-[8px] text-marine-offwhite/40 font-bold">E</div>
        <div className="absolute left-1 text-[8px] text-marine-offwhite/40 font-bold">W</div>
        
        {/* Needle */}
        <svg 
          className="w-10 h-10 text-marine-safe transition-transform duration-1000 ease-in-out" 
          style={{ transform: `rotate(${direction}deg)` }}
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <path d="M12 2v20M12 2l4 4M12 2L8 6" />
        </svg>
      </div>
      <div className="mt-2 text-xs font-mono text-marine-offwhite">{speed} km/h</div>
      <span className="text-[9px] text-marine-offwhite/60 uppercase tracking-widest font-semibold">{label}</span>
    </div>
  );
}

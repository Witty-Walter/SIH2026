import { useState } from "react";

export function LocationBar({ 
  onRequestLocation, 
  coords, 
  setCoords,
  error 
}: { 
  onRequestLocation: () => void, 
  coords: {lat: number, lon: number} | null,
  setCoords: (coords: {lat: number, lon: number}) => void,
  error: string | null 
}) {
  const [mockLat, setMockLat] = useState("13.0827");
  const [mockLon, setMockLon] = useState("80.2707");

  return (
    <div className="flex flex-col space-y-2 bg-marine-navy/60 backdrop-blur-md p-3 border border-marine-teal/40 rounded-2xl shadow-xl">
      
      {/* Top Row: Real GPS */}
      <div className="flex items-center space-x-4">
        <button 
          onClick={onRequestLocation}
          className="px-4 py-2 bg-marine-teal hover:bg-marine-teal/80 text-white rounded-full text-xs tracking-wider transition-all shadow font-semibold flex items-center space-x-2 active:scale-95"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.242-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          <span>GET GPS</span>
        </button>
        
        <div className="text-sm font-mono flex-1 text-marine-offwhite/90">
          {coords ? (
            <span className="text-marine-safe">Lat: {coords.lat.toFixed(4)}, Lon: {coords.lon.toFixed(4)}</span>
          ) : error ? (
            <span className="text-marine-danger">{error}</span>
          ) : (
            <span className="text-marine-offwhite/50">Location pending...</span>
          )}
        </div>
      </div>

      {/* Bottom Row: Mock Location for Admins */}
      <div className="flex items-center space-x-2 border-t border-marine-teal/20 pt-2 mt-2">
        <span className="text-[10px] text-marine-offwhite/50 font-bold uppercase tracking-widest mr-2">Admin Mock:</span>
        <input 
          type="text" 
          value={mockLat} 
          onChange={e => setMockLat(e.target.value)} 
          placeholder="Lat" 
          className="w-16 bg-marine-navy/50 border border-marine-teal/30 text-marine-offwhite text-xs p-1.5 rounded outline-none focus:border-marine-teal transition-colors"
        />
        <input 
          type="text" 
          value={mockLon} 
          onChange={e => setMockLon(e.target.value)} 
          placeholder="Lon" 
          className="w-16 bg-marine-navy/50 border border-marine-teal/30 text-marine-offwhite text-xs p-1.5 rounded outline-none focus:border-marine-teal transition-colors"
        />
        <button 
          onClick={() => setCoords({ lat: parseFloat(mockLat) || 13.0827, lon: parseFloat(mockLon) || 80.2707 })}
          className="px-3 py-1.5 bg-marine-navy hover:bg-marine-teal/50 border border-marine-teal/40 text-marine-offwhite rounded-full text-[10px] uppercase font-bold tracking-wider transition-all"
        >
          Set Mock
        </button>
      </div>

    </div>
  );
}

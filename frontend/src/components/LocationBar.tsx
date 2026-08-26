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
  const [mockLat, setMockLat] = useState("15.0");
  const [mockLon, setMockLon] = useState("70.0");

  return (
    <div className="flex flex-col space-y-2 bg-slate-800 p-3 rounded-lg border border-slate-700 shadow-sm">
      
      {/* Top Row: Real GPS */}
      <div className="flex items-center space-x-4">
        <button 
          onClick={onRequestLocation}
          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm transition-colors font-medium flex items-center space-x-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.242-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          <span>Get GPS</span>
        </button>
        
        <div className="text-sm font-mono text-slate-300 flex-1">
          {coords ? (
            <span className="text-green-400">Lat: {coords.lat.toFixed(4)}, Lon: {coords.lon.toFixed(4)}</span>
          ) : error ? (
            <span className="text-red-400">{error}</span>
          ) : (
            <span className="text-slate-500">Location not set</span>
          )}
        </div>
      </div>

      {/* Bottom Row: Mock Location for Admins */}
      <div className="flex items-center space-x-2 border-t border-slate-700 pt-2 mt-2">
        <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider mr-2">Admin Mock:</span>
        <input 
          type="text" 
          value={mockLat} 
          onChange={e => setMockLat(e.target.value)} 
          placeholder="Lat" 
          className="w-16 bg-slate-900 border border-slate-600 text-slate-200 text-xs p-1 rounded outline-none"
        />
        <input 
          type="text" 
          value={mockLon} 
          onChange={e => setMockLon(e.target.value)} 
          placeholder="Lon" 
          className="w-16 bg-slate-900 border border-slate-600 text-slate-200 text-xs p-1 rounded outline-none"
        />
        <button 
          onClick={() => setCoords({ lat: parseFloat(mockLat) || 15.0, lon: parseFloat(mockLon) || 70.0 })}
          className="px-2 py-1 bg-purple-600 hover:bg-purple-500 text-white rounded text-xs transition-colors font-medium"
        >
          Set Mock
        </button>
      </div>

    </div>
  );
}

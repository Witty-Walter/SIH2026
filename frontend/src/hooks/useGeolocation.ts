import { useState, useCallback } from "react";

export function useGeolocation() {
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [error, setError]   = useState<string | null>(null);

  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) { 
      setError("GPS not available in this browser."); 
      return; 
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      (err) => {
        console.warn(err);
        setError(`Location denied: ${err.message}. Using fallback.`);
        // Fallback to Chennai so the demo works for you
        setCoords({ lat: 13.0827, lon: 80.2707 }); 
      },
      { enableHighAccuracy: false, timeout: 15000, maximumAge: 10000 }
    );
  }, []);

  return { coords, setCoords, error, requestLocation };
}

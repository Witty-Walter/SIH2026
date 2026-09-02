"use client";

import { useState, useEffect } from "react";
import dynamic from 'next/dynamic';
import { LocationBar } from "@/components/LocationBar";
import { ChatPanel } from "@/components/ChatPanel";
import { AlertBanner } from "@/components/AlertBanner";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useGeolocation } from "@/hooks/useGeolocation";

// Map needs to be dynamically imported with SSR disabled because Leaflet uses the window object
const MapPanel = dynamic(() => import('@/components/MapPanel'), { ssr: false });

export default function Home() {
  const [sessionId, setSessionId] = useState("");
  
  useEffect(() => {
    // Generate simple session ID on mount
    setSessionId(Math.random().toString(36).substring(2, 15));
  }, []);

  const { coords, setCoords, error: gpsError, requestLocation } = useGeolocation();
  
  const { 
    streamingText, 
    finalText, 
    mapData, 
    alerts, 
    statusMsg, 
    isLoading, 
    sendMessage,
    stopGeneration
  } = useWebSocket(sessionId || "default-session");

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-marine-navy text-marine-offwhite font-sans">
      <AlertBanner alerts={alerts} />
      
      {/* Background Map */}
      <div className="absolute inset-0 z-0">
        <MapPanel mapData={mapData} userCoords={coords} />
      </div>

      {/* Floating Panels Overlay */}
      <div className="absolute inset-0 z-10 pointer-events-none flex justify-between p-4">
        
        {/* Left Panel: Chat / Decision Console */}
        <div className="pointer-events-auto h-full w-full max-w-md">
          <ChatPanel 
            streamingText={streamingText}
            finalText={finalText}
            statusMsg={statusMsg}
            isLoading={isLoading}
            mapData={mapData}
            sendMessage={sendMessage}
            stopGeneration={stopGeneration}
            userCoords={coords}
          />
        </div>

        {/* Right Panel: Top Controls */}
        <div className="pointer-events-auto">
          <LocationBar onRequestLocation={requestLocation} coords={coords} setCoords={setCoords} error={gpsError} />
        </div>
      </div>
    </main>
  );
}

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
    <main className="flex h-screen w-screen overflow-hidden bg-slate-900 text-slate-200 font-sans">
      <AlertBanner alerts={alerts} />
      
      {/* Left Panel: Chat */}
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

      {/* Right Panel: Map + Top Controls */}
      <div className="flex-1 relative flex flex-col h-full">
        <div className="absolute top-4 left-4 right-4 z-[400] flex justify-between pointer-events-none">
          {/* Controls overlaid on map */}
          <div className="pointer-events-auto">
            <LocationBar onRequestLocation={requestLocation} coords={coords} setCoords={setCoords} error={gpsError} />
          </div>
        </div>
        
        {/* The map itself */}
        <MapPanel mapData={mapData} userCoords={coords} />
      </div>
    </main>
  );
}

import { useState, useEffect, useRef, useCallback } from "react";
import { ServerFrame, ClientMessage, GeoJSONFeatureCollection, AlertFrame } from "@/types/api";

export function useWebSocket(sessionId: string) {
  const [streamingText, setStreamingText] = useState("");
  const [finalText, setFinalText]         = useState("");
  const [mapData, setMapData]             = useState<GeoJSONFeatureCollection | null>(null);
  const [alerts, setAlerts]               = useState<AlertFrame[]>([]);
  const [statusMsg, setStatusMsg]         = useState("");
  const [isLoading, setIsLoading]         = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    wsRef.current = new WebSocket(`ws://localhost:8000/ws/chat`);
    wsRef.current.onmessage = (event) => {
      const frame: ServerFrame = JSON.parse(event.data);
      switch (frame.type) {
        case "status":      
          setStatusMsg(frame.message); 
          break;
        case "alert":       
          setAlerts(prev => [...prev, frame]); 
          break;
        case "text_chunk":  
          setStreamingText(prev => prev + frame.chunk); 
          break;
        case "map_update":  
          setMapData(frame.data); 
          break;
        case "done":
          setStreamingText(currentStreaming => {
            setFinalText(currentStreaming);
            return ""; 
          });
          setIsLoading(false); 
          setStatusMsg(""); 
          break;
        case "error":
          setStatusMsg(`Error: ${frame.message}`);
          setIsLoading(false);
          break;
      }
    };
    
    wsRef.current.onclose = () => {
      setIsLoading(false);
      setStatusMsg(prev => prev.startsWith("Error:") ? prev : "Connection closed.");
    };

    wsRef.current.onerror = () => {
      setIsLoading(false);
      setStatusMsg("Connection error.");
    };
  }, []);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  const sendMessage = useCallback((text: string, lat: number, lon: number) => {
    const msg: ClientMessage = {
      type: "message", text, session_id: sessionId,
      context: { user_lat: lat, user_lon: lon, location_source: "gps" }
    };
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      setStatusMsg("Connecting to server... please try again in a moment.");
      return;
    }
    
    setIsLoading(true); 
    setStreamingText(""); 
    setAlerts([]);
    wsRef.current?.send(JSON.stringify(msg));
  }, [sessionId]);

  const stopGeneration = useCallback(() => {
    setIsLoading(false);
    setStatusMsg("");
    wsRef.current?.close();
    connect(); // Reconnect immediately for the next message
  }, [connect]);

  return { streamingText, finalText, mapData, alerts, statusMsg, isLoading, sendMessage, stopGeneration };
}

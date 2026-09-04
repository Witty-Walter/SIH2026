import { useState, useRef, useEffect } from "react";
import { MessageBubble } from "./MessageBubble";
import { GeoJSONFeatureCollection } from "@/types/api";

interface ChatPanelProps {
  streamingText: string;
  finalText: string;
  statusMsg: string;
  isLoading: boolean;
  mapData: GeoJSONFeatureCollection | null;
  sendMessage: (text: string, lat: number, lon: number) => void;
  stopGeneration: () => void;
  userCoords: { lat: number; lon: number } | null;
}

export function ChatPanel({ streamingText, finalText, statusMsg, isLoading, mapData, sendMessage, stopGeneration, userCoords }: ChatPanelProps) {
  const [input, setInput] = useState("");
  // Simple local state to keep track of user messages for the UI
  const [history, setHistory] = useState<{role: "user"|"assistant", text: string, status?: string, pfzStatus?: string, fishingScore?: number}[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // When final text arrives from backend, append it to history
  useEffect(() => {
    if (finalText) {
      // Find the status from mapData if available
      let riskStatus = "UNKNOWN";
      let pfzStatus = "UNKNOWN";
      let fishingScore = 0;
      if (mapData && mapData.features.length > 0) {
         const validRiskStatuses = ["SAFE", "CAUTION", "UNSAFE"];
         
         let target = mapData.features.find(f => f.properties.label === "Target Area" && validRiskStatuses.includes(f.properties.status || ""));
         if (!target) {
            target = mapData.features.find(f => f.properties.label && f.properties.label.includes("RECOMMENDED") && validRiskStatuses.includes(f.properties.status || ""));
         }
         if (!target) {
            target = mapData.features.find(f => f.properties.status && validRiskStatuses.includes(f.properties.status || ""));
         }
         
         if (target && target.properties.status) riskStatus = target.properties.status;
         
         // Extract PFZ / Fishing Status
         const pfzTarget = mapData.features.find(f => f.properties.status && ["HIGH", "MEDIUM", "LOW"].includes(f.properties.status || ""));
         if (pfzTarget && pfzTarget.properties.status) {
             pfzStatus = pfzTarget.properties.status;
             if (pfzStatus === "HIGH") fishingScore = 85;
             else if (pfzStatus === "MEDIUM") fishingScore = 55;
             else if (pfzStatus === "LOW") fishingScore = 25;
         } else {
             const labelTarget = mapData.features.find(f => f.properties.label && f.properties.label.includes("Fishing:"));
             if (labelTarget) {
                 const match = labelTarget.properties.label.match(/Fishing:\s*(\d+)/);
                 if (match) {
                     fishingScore = parseInt(match[1]);
                     if (fishingScore >= 70) pfzStatus = "HIGH";
                     else if (fishingScore >= 40) pfzStatus = "MEDIUM";
                     else pfzStatus = "LOW";
                 }
             }
         }
      }
      setHistory(prev => {
        const newHistory = [...prev];
        const lastItem = newHistory[newHistory.length - 1];
        if (lastItem && lastItem.role === "assistant" && lastItem.text === finalText) {
          // Update the existing item with new map statuses
          lastItem.status = riskStatus;
          lastItem.pfzStatus = pfzStatus;
          lastItem.fishingScore = fishingScore;
          return newHistory;
        } else {
          // Append new item
          return [...newHistory, { role: "assistant", text: finalText, status: riskStatus, pfzStatus, fishingScore }];
        }
      });
    }
  }, [finalText, mapData]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history, streamingText]);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    setHistory(prev => [...prev, { role: "user", text: input }]);
    sendMessage(input, userCoords?.lat || 0, userCoords?.lon || 0);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full bg-marine-navy/60 backdrop-blur-2xl border border-marine-teal/40 rounded-3xl shadow-[0_0_40px_rgba(0,0,0,0.5)] relative z-10 overflow-hidden">
      
      {/* Header */}
      <div className="p-5 border-b border-marine-teal/30 bg-marine-navy/40 shrink-0 flex items-center space-x-3">
        <div className="w-12 h-12 flex items-center justify-center shrink-0">
           <img src="/logo.png" alt="Marine Intel Logo" className="w-full h-full object-contain drop-shadow-[0_0_15px_rgba(27,107,120,0.5)]" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-wide text-marine-offwhite">MARINE<span className="text-marine-teal font-light">INTEL</span></h1>
          <p className="text-[10px] text-marine-offwhite/50 uppercase tracking-widest font-semibold">Safety Console Active</p>
        </div>
      </div>

      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 space-y-6">
        {history.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} text={msg.text} status={msg.status} pfzStatus={msg.pfzStatus} fishingScore={msg.fishingScore} />
        ))}
        
        {/* Streaming message */}
        {streamingText && (
          <MessageBubble role="assistant" text={streamingText} />
        )}
        
        {/* Loading Indicator */}
        {isLoading && !streamingText && (
          <div className="flex items-center space-x-2 text-marine-teal text-sm p-4 bg-marine-navy/30 rounded-2xl border border-marine-teal/20 w-fit">
            <div className="w-2 h-2 bg-marine-teal rounded-full animate-pulse" />
            <div className="w-2 h-2 bg-marine-teal rounded-full animate-pulse" style={{ animationDelay: "150ms" }} />
            <div className="w-2 h-2 bg-marine-teal rounded-full animate-pulse" style={{ animationDelay: "300ms" }} />
            <span className="ml-2 font-mono text-xs text-marine-offwhite/70 uppercase tracking-widest">{statusMsg || "AWAITING TELEMETRY..."}</span>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-marine-navy/80 shrink-0 border-t border-marine-teal/30">
        <div className="flex items-end space-x-3">
          <div className="flex-1 bg-marine-navy/50 border border-marine-teal/40 rounded-2xl overflow-hidden focus-within:border-marine-teal focus-within:ring-1 focus-within:ring-marine-teal transition-all shadow-inner">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
              }}
              placeholder="Query safety conditions or fishing zones..."
              className="w-full max-h-32 min-h-[44px] bg-transparent text-sm text-marine-offwhite placeholder-marine-offwhite/30 p-3.5 outline-none resize-none font-mono"
              rows={1}
            />
          </div>
          {isLoading ? (
            <button
              onClick={stopGeneration}
              className="p-3.5 bg-marine-danger hover:bg-red-500 text-marine-offwhite rounded-2xl transition-all shadow-lg active:scale-95 flex items-center justify-center shrink-0"
              title="Stop generating"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" /></svg>
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="p-3.5 bg-gradient-to-r from-marine-teal to-blue-500 hover:from-marine-teal/80 hover:to-blue-500/80 disabled:from-marine-navy disabled:to-marine-navy disabled:border disabled:border-marine-teal/20 disabled:text-marine-offwhite/30 text-white rounded-2xl transition-all shadow-lg active:scale-95 flex items-center justify-center shrink-0"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

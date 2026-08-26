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
  const [history, setHistory] = useState<{role: "user"|"assistant", text: string, status?: string}[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // When final text arrives from backend, append it to history
  useEffect(() => {
    if (finalText) {
      // Find the status from mapData if available
      let riskStatus = "UNKNOWN";
      if (mapData && mapData.features.length > 0) {
         const target = mapData.features.find(f => f.properties.label === "Target Area");
         if (target) riskStatus = target.properties.status || "UNKNOWN";
      }
      setHistory(prev => [...prev, { role: "assistant", text: finalText, status: riskStatus }]);
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
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800 w-full max-w-md shadow-2xl relative z-10">
      
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-900/95 backdrop-blur shrink-0 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">Marine Intel</h1>
          <p className="text-xs text-slate-400">Agentic Safety & PFZ AI</p>
        </div>
      </div>

      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {history.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} text={msg.text} status={msg.status} />
        ))}
        
        {/* Streaming message */}
        {streamingText && (
          <MessageBubble role="assistant" text={streamingText} />
        )}
        
        {/* Loading Indicator */}
        {isLoading && !streamingText && (
          <div className="flex items-center space-x-2 text-slate-500 text-sm p-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            <span className="ml-2 font-mono text-xs">{statusMsg || "Thinking..."}</span>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-slate-800/50 backdrop-blur shrink-0 border-t border-slate-700">
        <div className="flex items-end space-x-2">
          <div className="flex-1 bg-slate-900 border border-slate-700 rounded-xl overflow-hidden focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all shadow-inner">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
              }}
              placeholder="Ask about fishing zones, safety, or weather..."
              className="w-full max-h-32 min-h-[44px] bg-transparent text-sm text-slate-200 placeholder-slate-500 p-3 outline-none resize-none"
              rows={1}
            />
          </div>
          {isLoading ? (
            <button
              onClick={stopGeneration}
              className="p-3 bg-red-600 hover:bg-red-500 text-white rounded-xl transition-all shadow-md active:scale-95 flex items-center justify-center shrink-0"
              title="Stop generating"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" /></svg>
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="p-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-xl transition-all shadow-md active:scale-95 flex items-center justify-center shrink-0"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

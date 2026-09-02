import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { RadialGauge } from './instruments/RadialGauge';
import { CompassNeedle } from './instruments/CompassNeedle';
import { Sparkline } from './instruments/Sparkline';
import { Droplet } from './instruments/Droplet';

// Helper to parse the AI's markdown table into telemetry data
function parseTelemetry(text: string) {
  let safetyScore = 85;
  let windSpeed = 15;
  let windDirection = 135; // SE
  let waveHeight = 1.2;
  let precipitation = 0;
  let hasTelemetry = false;
  let textStatus = "UNKNOWN";
  
  // Very basic regex extraction for the demo
  const safetyMatch = text.match(/Safety score.*?(\d+)\/100/i);
  if (safetyMatch) { safetyScore = parseInt(safetyMatch[1]); hasTelemetry = true; }
  
  const statusMatch = text.match(/(Risk )?Status.*?(\bSAFE\b|\bCAUTION\b|\bUNSAFE\b)/i);
  if (statusMatch) { textStatus = statusMatch[2].toUpperCase(); hasTelemetry = true; }
  
  const windMatch = text.match(/Wind.*?(\d+)\s*km\/h/i);
  if (windMatch) { windSpeed = parseInt(windMatch[1]); hasTelemetry = true; }

  const waveMatch = text.match(/Wave.*?(\d+(\.\d+)?)\s*m/i);
  if (waveMatch) { waveHeight = parseFloat(waveMatch[1]); hasTelemetry = true; }

  const precipMatch = text.match(/Precipitation.*?(\d+)\s*%/i);
  if (precipMatch) { precipitation = parseInt(precipMatch[1]); hasTelemetry = true; }

  // Clean the text by removing the markdown table
  const cleanText = text.replace(/\|.*\|/g, '').replace(/[\r\n]{2,}/g, '\n\n').trim();

  return { safetyScore, windSpeed, windDirection, waveHeight, precipitation, hasTelemetry, cleanText, textStatus };
}

export function MessageBubble({ role, text, status, pfzStatus, fishingScore: propFishingScore }: { role: "user" | "assistant", text: string, status?: string, pfzStatus?: string, fishingScore?: number }) {
  const isUser = role === "user";
  
  const { safetyScore, windSpeed, windDirection, waveHeight, precipitation, hasTelemetry, cleanText, textStatus } = parseTelemetry(text);
  
  const finalStatus = (status && status !== "UNKNOWN") ? status : ((textStatus !== "UNKNOWN") ? textStatus : "UNKNOWN");
  
  let statusColor = "text-marine-offwhite";
  if (finalStatus === "SAFE") statusColor = "text-marine-safe";
  if (finalStatus === "CAUTION") statusColor = "text-marine-caution";
  if (finalStatus === "UNSAFE") statusColor = "text-marine-danger";
  if (finalStatus === "UNKNOWN") statusColor = "text-marine-offwhite/50";

  const displayStatus = finalStatus === "UNKNOWN" ? "PENDING" : finalStatus;

  const finalPfzStatus = (pfzStatus && pfzStatus !== "UNKNOWN") ? pfzStatus : "UNKNOWN";
  let pfzStatusColor = "text-marine-offwhite";
  if (finalPfzStatus === "HIGH") pfzStatusColor = "text-marine-safe";
  if (finalPfzStatus === "MEDIUM") pfzStatusColor = "text-marine-caution";
  if (finalPfzStatus === "LOW") pfzStatusColor = "text-marine-danger";
  if (finalPfzStatus === "UNKNOWN") pfzStatusColor = "text-marine-offwhite/50";
  
  const displayPfzStatus = finalPfzStatus === "UNKNOWN" ? "PENDING" : finalPfzStatus;
  const finalFishingScore = propFishingScore !== undefined && propFishingScore > 0 ? propFishingScore : 0;

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-6`}>
      <div className={`max-w-[90%] rounded-2xl px-5 py-4 shadow-xl border ${
        isUser 
          ? "bg-gradient-to-br from-marine-teal to-blue-600 text-white rounded-tr-sm border-marine-teal/50" 
          : "bg-marine-navy/70 backdrop-blur-md border-marine-teal/30 text-marine-offwhite rounded-tl-sm"
      }`}>
        
        {/* HERO READOUT & INSTRUMENTS (Only for AI with status/telemetry) */}
        {!isUser && hasTelemetry && (
          <div className="mb-4 pb-4 border-b border-marine-teal/20">
            {/* Hero Readout */}
            <div className="flex items-center space-x-4 mb-4 overflow-x-auto pb-1 scrollbar-hide">
              <div className="bg-marine-navy/40 px-5 py-3 rounded-2xl border border-marine-teal/10 shrink-0 min-w-[160px]">
                <div className="text-[10px] text-marine-offwhite/50 uppercase tracking-widest font-bold mb-1">Risk Status</div>
                <div className={`text-2xl font-bold tracking-tight ${statusColor}`}>
                  {displayStatus}
                </div>
              </div>
              
              <div className="bg-marine-navy/40 px-5 py-3 rounded-2xl border border-marine-teal/10 shrink-0 min-w-[160px]">
                <div className="text-[10px] text-marine-offwhite/50 uppercase tracking-widest font-bold mb-1">Finding Prob.</div>
                <div className={`text-2xl font-bold tracking-tight ${pfzStatusColor}`}>
                  {displayPfzStatus}
                </div>
              </div>
            </div>
            
            {/* Instrument Row */}
            <div className="flex space-x-3 overflow-x-auto pb-2 scrollbar-hide">
               <CompassNeedle direction={windDirection} speed={windSpeed} label="Wind" />
               {/* Simulate wave sparkline data around the current height */}
               <Sparkline data={[waveHeight-0.2, waveHeight+0.1, waveHeight-0.1, waveHeight+0.3, waveHeight]} label="Waves" unit="m" />
               <Droplet intensity={precipitation} label="Precip" />
            </div>
          </div>
        )}

        {/* Regular Text */}
        <div className={`text-sm leading-relaxed ${isUser ? 'whitespace-pre-wrap' : 'prose prose-invert max-w-none prose-sm prose-p:text-marine-offwhite/90 prose-li:text-marine-offwhite/90'}`}>
          {isUser ? (
            text
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {hasTelemetry ? cleanText : text}
            </ReactMarkdown>
          )}
        </div>
      </div>
    </div>
  );
}

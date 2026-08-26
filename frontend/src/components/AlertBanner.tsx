import { AlertFrame } from "@/types/api";
import { useEffect, useState } from "react";

export function AlertBanner({ alerts }: { alerts: AlertFrame[] }) {
  const [activeAlerts, setActiveAlerts] = useState<AlertFrame[]>([]);

  useEffect(() => {
    setActiveAlerts(alerts);
    if (alerts.length > 0) {
      const timer = setTimeout(() => setActiveAlerts([]), 10000); // dismiss after 10s
      return () => clearTimeout(timer);
    }
  }, [alerts]);

  if (activeAlerts.length === 0) return null;

  return (
    <div className="absolute top-0 left-0 right-0 z-[1000] p-4 flex flex-col items-center pointer-events-none">
      {activeAlerts.map((alert, idx) => (
        <div key={idx} className={`mb-2 px-6 py-3 rounded-lg shadow-xl pointer-events-auto border-2 ${
          alert.severity === 3 ? "bg-red-900 border-red-500 text-red-50 animate-pulse" :
          alert.severity === 2 ? "bg-orange-900 border-orange-500 text-orange-50" :
          "bg-blue-900 border-blue-500 text-blue-50"
        }`}>
          <div className="flex items-center space-x-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <div className="font-bold uppercase tracking-wider text-sm">{alert.alert_type} WARNING</div>
              <div className="text-sm opacity-90">{alert.message}</div>
            </div>
            <button 
              onClick={() => setActiveAlerts(prev => prev.filter((_, i) => i !== idx))}
              className="ml-4 opacity-50 hover:opacity-100"
            >×</button>
          </div>
        </div>
      ))}
    </div>
  );
}

"use client";
// We need "use client" because react-leaflet relies on window object which breaks SSR

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { GeoJSONFeatureCollection, GeoJSONFeature } from "@/types/api";

function styleFeature(feature: any) {
  const p = feature.properties;
  return { 
    color: p.color || "#3388ff", 
    fillColor: p.color || "#3388ff", 
    fillOpacity: p.fill_opacity || 0.2, 
    weight: 2,
    dashArray: p.status === "RESTRICTED" ? "5, 5" : ""
  };
}

export default function MapPanel({ 
  mapData, 
  userCoords 
}: { 
  mapData: GeoJSONFeatureCollection | null,
  userCoords: {lat: number, lon: number} | null
}) {
  // Use a key derived from mapData to force full GeoJSON layer remount on each update
  const layerKey = mapData ? JSON.stringify(mapData).slice(0, 64) : "empty";
  
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    // Fix Leaflet marker icon issue in Next.js
    import('leaflet').then(L => {
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
      });
      setMounted(true);
    });
  }, []);

  if (!mounted) return <div className="h-full w-full bg-slate-800 animate-pulse flex items-center justify-center">Loading Map...</div>;

  return (
    <div className="relative h-full w-full bg-slate-800">
      <MapContainer 
        center={[15.0, 74.0]} 
        zoom={5} 
        className="h-full w-full z-0"
        zoomControl={false}
      >
        <TileLayer 
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        
        {mapData && (
          <GeoJSON 
            key={layerKey} 
            data={mapData as any} 
            style={styleFeature}
            onEachFeature={(feature: any, layer: any) => {
              const p = feature.properties;
              let popupContent = `<div style="color: #333; font-family: sans-serif;">`;
              popupContent += `<h3 style="margin:0 0 4px 0; font-size: 14px; font-weight: bold;">${p.label}</h3>`;
              if (p.status) popupContent += `<div><b>Status:</b> ${p.status}</div>`;
              if (p.safety_score) popupContent += `<div><b>Safety:</b> ${p.safety_score}/100</div>`;
              if (p.fishing_score) popupContent += `<div><b>Fishing:</b> ${p.fishing_score}/100</div>`;
              popupContent += `</div>`;
              layer.bindPopup(popupContent);
            }}
          />
        )}

        {userCoords && (
          <Marker position={[userCoords.lat, userCoords.lon]}>
            <Popup>
              <div style={{ color: "#333", fontFamily: "sans-serif" }}>
                <h3 style={{ margin: "0 0 4px 0", fontSize: "14px", fontWeight: "bold" }}>Your Location</h3>
                <div>Lat: {userCoords.lat.toFixed(4)}</div>
                <div>Lon: {userCoords.lon.toFixed(4)}</div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
      
      {/* Overlay map controls here if needed */}
    </div>
  );
}

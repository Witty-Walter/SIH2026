"use client";
// We need "use client" because react-leaflet relies on window object which breaks SSR

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { GeoJSONFeatureCollection, GeoJSONFeature } from "@/types/api";

function styleFeature(feature: any) {
  const p = feature.properties;
  
  let baseColor = "#3F3F46"; // marine teal (zinc-700)
  if (p.status === "SAFE") baseColor = "#3FA66E";
  else if (p.status === "CAUTION") baseColor = "#E08A2C";
  else if (p.status === "UNSAFE" || p.status === "RESTRICTED") baseColor = "#D93838";

  return { 
    color: baseColor, 
    fillColor: baseColor, 
    fillOpacity: 0.25, 
    weight: p.status === "RESTRICTED" ? 2 : 1,
    dashArray: p.status === "RESTRICTED" ? "5, 5" : "",
    className: 'transition-all duration-500 hover:fill-opacity-50' // Add a little Tailwind hover magic if supported by the SVG
  };
}

function BoundsFitter({ data, userCoords }: { data: any, userCoords: any }) {
  const map = useMap();
  useEffect(() => {
    if (!data && !userCoords) return;
    
    const bounds = L.latLngBounds([]);
    if (userCoords) {
      bounds.extend([userCoords.lat, userCoords.lon]);
    }
    
    if (data && data.features) {
      data.features.forEach((f: any) => {
        if (f.geometry.type === 'Point') {
          bounds.extend([f.geometry.coordinates[1], f.geometry.coordinates[0]]);
        } else if (f.geometry.type === 'Polygon') {
          f.geometry.coordinates[0].forEach((coord: any) => {
             bounds.extend([coord[1], coord[0]]);
          });
        }
      });
    }
    
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
    }
  }, [data, userCoords, map]);
  return null;
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

  if (!mounted) return <div className="h-full w-full bg-marine-navy animate-pulse flex items-center justify-center font-mono text-marine-teal">INITIALIZING TELEMETRY...</div>;

  return (
    <div className="relative h-full w-full bg-marine-navy">
      <MapContainer 
        center={[15.0, 74.0]} 
        zoom={5} 
        className="h-full w-full z-0"
        zoomControl={false}
      >
        <TileLayer 
          url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
          attribution='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
        />
        
        <BoundsFitter data={mapData} userCoords={userCoords} />

        {mapData && (
          <GeoJSON 
            key={layerKey} 
            data={mapData as any} 
            style={styleFeature}
            onEachFeature={(feature: any, layer: any) => {
              const p = feature.properties;
              let popupContent = `<div class="font-sans text-marine-offwhite">`;
              popupContent += `<h3 class="m-0 mb-2 pb-1 border-b border-marine-teal/30 text-sm font-bold tracking-wider uppercase">${p.label}</h3>`;
              
              if (p.status) {
                let color = "#F4F7F5";
                if (p.status === "SAFE") color = "#3FA66E";
                if (p.status === "CAUTION") color = "#E08A2C";
                if (p.status === "UNSAFE" || p.status === "RESTRICTED") color = "#D93838";
                popupContent += `<div class="flex justify-between items-center text-xs mb-1">
                                   <span class="text-marine-offwhite/50 uppercase font-bold tracking-widest text-[9px]">Status</span>
                                   <span style="color: ${color}" class="font-bold tracking-widest">${p.status}</span>
                                 </div>`;
              }
              if (p.safety_score) {
                popupContent += `<div class="flex justify-between items-center text-xs mb-1">
                                   <span class="text-marine-offwhite/50 uppercase font-bold tracking-widest text-[9px]">Safety</span>
                                   <span class="font-mono font-bold">${p.safety_score}/100</span>
                                 </div>`;
              }
              if (p.fishing_score) {
                popupContent += `<div class="flex justify-between items-center text-xs">
                                   <span class="text-marine-offwhite/50 uppercase font-bold tracking-widest text-[9px]">Fishing</span>
                                   <span class="font-mono font-bold">${p.fishing_score}/100</span>
                                 </div>`;
              }
              popupContent += `</div>`;
              layer.bindPopup(popupContent);
            }}
          />
        )}

        {userCoords && (
          <Marker position={[userCoords.lat, userCoords.lon]}>
            <Popup>
              <div className="font-sans text-marine-offwhite">
                <h3 className="m-0 mb-2 pb-1 border-b border-marine-teal/30 text-sm font-bold tracking-wider uppercase text-marine-teal">Current Location</h3>
                <div className="flex justify-between items-center text-xs mb-1">
                   <span className="text-marine-offwhite/50 uppercase font-bold tracking-widest text-[9px] mr-4">Lat</span>
                   <span className="font-mono font-bold">{userCoords.lat.toFixed(4)}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                   <span className="text-marine-offwhite/50 uppercase font-bold tracking-widest text-[9px] mr-4">Lon</span>
                   <span className="font-mono font-bold">{userCoords.lon.toFixed(4)}</span>
                </div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
      
      {/* Overlay map controls here if needed */}
    </div>
  );
}

export type FrameType = "status" | "alert" | "text_chunk" | "map_update" | "done" | "error";

export interface StatusFrame   { type: "status"; message: string; }
export interface AlertFrame    { type: "alert"; severity: 1|2|3; alert_type: string; message: string; }
export interface TextChunkFrame { type: "text_chunk"; chunk: string; }
export interface MapUpdateFrame { type: "map_update"; data: GeoJSONFeatureCollection; }
export interface DoneFrame     { type: "done"; }

export interface ErrorFrame    { type: "error"; message: string; }

export type ServerFrame = StatusFrame | AlertFrame | TextChunkFrame | MapUpdateFrame | DoneFrame | ErrorFrame;

export interface ClientMessage {
  type: "message";
  text: string;
  context: { user_lat: number; user_lon: number; location_source: "gps"|"pin"|"manual" };
  session_id: string;
}

export interface GeoJSONFeature {
  type: "Feature";
  geometry: { type: "Polygon"|"Point"|"LineString"; coordinates: number[][][] | number[] };
  properties: {
    id?: string;
    label: string;
    status?: "SAFE"|"CAUTION"|"UNSAFE"|"RESTRICTED"|"PFZ";
    color?: string;
    fill_opacity?: number;
    safety_score?: number;
    fishing_score?: number;
    icon?: string;
  };
}
export interface GeoJSONFeatureCollection { type: "FeatureCollection"; features: GeoJSONFeature[]; }

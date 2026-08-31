from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from db.connection import db
from agents.graph import build_graph
from app.api.marine_routes import router as marine_router
from app.services.imd.client import fetch_and_store_imd_alerts
from app.services.incois.client import fetch_and_store_incois_pfz
import json
import uuid
import asyncio

app = FastAPI(title="Marine Intelligence API")

app.include_router(marine_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

@app.on_event("startup")
async def startup():
    await db.connect()
    # Fetch live IMD cyclone alerts and compute PFZs on startup
    await fetch_and_store_imd_alerts()
    await fetch_and_store_incois_pfz()
    
    async def _refresh_alerts_loop():
        while True:
            await asyncio.sleep(6 * 3600)
            await fetch_and_store_imd_alerts()
            await fetch_and_store_incois_pfz()
            
    asyncio.create_task(_refresh_alerts_loop())

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.post("/admin/refresh-pfz")
async def admin_refresh_pfz():
    """Admin endpoint to manually trigger PFZ computation for demos."""
    count = await fetch_and_store_incois_pfz()
    return {"status": "success", "inserted_zones": count}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Simple in-memory session store for MVP
    # In production, this would load/save from the PostGIS `conversations` table
    session_state = {
        "messages": [],
        "user_language": "en",
        "current_location": {},
        "selected_area_id": None
    }
    
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            if data.get("type") == "message":
                user_text = data.get("text", "")
                context = data.get("context", {})
                
                # Update location context from client GPS if available
                if "user_lat" in context and "user_lon" in context:
                    session_state["current_location"]["user_lat"] = context["user_lat"]
                    session_state["current_location"]["user_lon"] = context["user_lon"]
                
                # Add human message
                from langchain_core.messages import HumanMessage
                session_state["messages"].append(HumanMessage(content=user_text))
                
                # Send status frame
                await websocket.send_json({"type": "status", "message": "Analyzing request..."})
                
                # Run graph
                final_state = await graph.ainvoke(session_state)
                
                # Update session state for next turn
                session_state["user_language"] = final_state.get("user_language", "en")
                if final_state.get("selected_area_id"):
                    session_state["selected_area_id"] = final_state.get("selected_area_id")
                # Persist location context so user_lat/lon are available on future turns
                if final_state.get("current_location"):
                    session_state["current_location"] = final_state.get("current_location")
                    
                # Stream back map updates and text
                if "map_data" in final_state:
                    await websocket.send_json({
                        "type": "map_update",
                        "data": final_state["map_data"]
                    })
                    
                # Send live cyclone alert if GIS detected one
                gis_data = final_state.get("gis_data", {})
                if gis_data.get("cyclone_alert"):
                    await websocket.send_json({
                        "type": "alert",
                        "severity": gis_data.get("cyclone_alert_severity", 3),
                        "alert_type": "CYCLONE",
                        "message": gis_data.get("cyclone_alert_title", "IMD Cyclone Warning active in this area!")
                    })
                elif final_state.get("risk_result", {}).get("status") == "UNSAFE":
                    await websocket.send_json({
                        "type": "alert",
                        "severity": 3,
                        "alert_type": "DANGER",
                        "message": "The requested area is unsafe."
                    })
                    
                response_text = final_state.get("response_text", "I'm sorry, I couldn't process that.")
                
                # Simulate text chunk streaming
                chunk_size = 10
                for i in range(0, len(response_text), chunk_size):
                    await websocket.send_json({
                        "type": "text_chunk",
                        "chunk": response_text[i:i+chunk_size]
                    })
                    import asyncio
                    await asyncio.sleep(0.01)
                    
                # Add AI message to history
                from langchain_core.messages import AIMessage
                session_state["messages"].append(AIMessage(content=response_text))
                
                await websocket.send_json({"type": "done"})
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
        await websocket.close()

import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        msg = {
            "type": "message",
            "text": "can i go to fishing today at 4 PM",
            "context": { "user_lat": 0, "user_lon": 0, "location_source": "gps" }
        }
        await websocket.send(json.dumps(msg))
        
        while True:
            try:
                response = await websocket.recv()
                print(f"Received data chunk")
                data = json.loads(response)
                if data.get("type") in ["done", "error"]:
                    print(f"Final response: {data}")
                    break
            except Exception as e:
                print(f"Error receiving: {e}")
                break

if __name__ == "__main__":
    asyncio.run(test_ws())

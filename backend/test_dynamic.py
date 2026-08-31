import asyncio
from agents.nodes.context import context_node
from db.connection import db

async def test():
    await db.connect()
    state = {
        'intent': {'entities': {}},
        'current_location': {'user_lat': 8.08, 'user_lon': 77.538}
    }
    # This will trigger the fallback bbox creation around the user point
    res = await context_node(state)
    print("Number of dynamic PFZs found:", len(res.get('dynamic_pfzs', [])))
    if res.get('dynamic_pfzs'):
        print("Sample:", res['dynamic_pfzs'][0]['properties'])
    await db.disconnect()

asyncio.run(test())

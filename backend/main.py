import asyncio

import simpy
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from simulation import ParkingSimulation

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Frontend terhubung! Memulai simulasi real-time...")

    env = simpy.Environment()
    sim = ParkingSimulation(env)
    sim.start()

    next_step = 1.0

    try:
        while True:
            env.run(until=next_step)
            if sim.events:
                for event in sim.events:
                    await websocket.send_json(event)

                sim.events = []

            await asyncio.sleep(0.5)

            next_step += 1.0

    except WebSocketDisconnect:
        print("Frontend putus koneksi.")
    except Exception as e:
        print(f"Error: {e}")

import asyncio
import websockets

async def client_handler(websocket,path):
    print("New Client Connected")
    try:
        while True:
            None
    except websockets.ConnectionClosed as err:
        print(err)
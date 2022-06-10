import asyncio
from urllib import response
import websockets
from websockets.exceptions import ConnectionClosed
import time
import binascii

import src.socket_server.socket_handler as socket_handler
import src.ESP8266.ESP8266_01_device as ESP8266_01_device
import src.smart_home_api.smart_home_api as smart_home_api

async def client_handler(websocket):
    print("New Client Connected")
    try:
        # On connect message
        on_connect = await websocket.recv()
        print(on_connect)

        # Request info about device
        await websocket.send(ESP8266_01_device.ESP8266_01.REQUEST_WHO_HEADER)
        response_who = await websocket.recv()
        print("Received RESPONSE_WHO: "+str(response_who))
        hwid = ESP8266_01_device.ESP8266_01.get_hwid(response_who)
        device_class = smart_home_api.check_device_class(hwid)
        if hwid == 4:
            print("OK")
        device = None
        if device_class == None:
            websocket.disconnect()
        elif device_class == ESP8266_01_device.ESP8266_01_Type.Relay_Device:
            print("Connected Relay device")
            device = ESP8266_01_device.Relay_Device(hwid,1)
        elif device_class == ESP8266_01_device.ESP8266_01_Type.DHT22:
            print("Connected DHT22 Sensor")
            device = ESP8266_01_device.DHT22_Device(hwid)
        else:
            print("Unknown device connected!")
        while True:
            print("Looop move")
            device.update_commands()
            commands = device.get_commands()
            while not commands.empty():
                command = commands.get()
                print("Sending command: "+str(command))
                await websocket.send(command)
                response = await websocket.recv()
                print("Received data: "+str(response))
                device.handle_data(response)
            time.sleep(5.0)
    except ConnectionClosed as err:
        websocket.close()
        print("Disconnecting - connection closed")

if __name__ == "__main__":
    print("Started server")
    server = websockets.serve(client_handler,'0.0.0.0',12023)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
    
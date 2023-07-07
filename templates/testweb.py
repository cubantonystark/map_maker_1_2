import http.server
import socketserver
import asyncio
import websockets

PORT = 8000

async def send_object_position(websocket, path):
    while True:
        position = ("0", "0")     # Function to get the object's position
        await websocket.send(str(position))
        await asyncio.sleep(1)  # Send position every second

async def serve_http():
    server = socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler)
    await server.serve_forever()

async def start_websocket_server():
    websocket_server = websockets.serve(send_object_position, "localhost", PORT)
    await websocket_server

async def main():
    await asyncio.gather(start_websocket_server(), serve_http())

if __name__ == "__main__":
    asyncio.run(main())
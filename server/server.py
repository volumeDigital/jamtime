import asyncio
import websockets

clients = set()

async def broadcast(data):
    for ws in clients:
        try:
            await ws.send(data)
        except websockets.exceptions.ConnectionClosed:
            pass

async def conn(reader, writer):
    _ = await reader.read(1024)

    head = b"HTTP/1.1 200 OK\r\n"
    head += b"Content-Type: text/html\r\n"
    head += b"\r\n"

    with open('index.html', 'rb') as f:
        body = f.read()
        writer.write(head + body)
        writer.close()

async def webserver(host, port):
    srv = await asyncio.start_server(conn, host, port)
    async with srv:
        await srv.serve_forever()

async def echo(websocket, path):
    clients.add(websocket)
    try:
        while True:
            data = await websocket.recv()
            await broadcast("alert")
            await websocket.send(data + " reply!")
    except websockets.exceptions.ConnectionClosed:
        clients.remove(websocket)

async def main():
    await asyncio.gather(
        webserver('0.0.0.0', 8000),
        websockets.serve(echo, "0.0.0.0", 8765)
        )

asyncio.run(main())


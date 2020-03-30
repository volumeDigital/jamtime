import asyncio
import websockets
import json

clients = set()
fragments = list()

def makeDoc():
    doc = dict()
    doc["name"]         = "demo"
    doc["fragments"]    = list()

    for f in fragments:
        doc["fragments"].append(f)

    return json.dumps(doc)

async def update():
    doc = makeDoc()
    for c in clients:
        try:
            await c.send(doc)
        except websockets.exceptions.ConnectionClosed:
            clients.remove(c)

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

            j = json.loads(data)

            action = j["action"]

            if action  == "attach":

                print("attach")
                await websocket.send(makeDoc())

            elif action == "add_fragment":

                print("add_fragment")
                fragment = j["fragment"]
                print(fragment)
                fragments.append(fragment)
                await update()

            elif action == "del_fragment":

                print("del_fragment")
                fragment = j["fragment"]
                print(fragment)

                for f in fragments:
                    if f == fragment:
                        fragments.remove(f)
                        break

                await update()

            else:
                print("unknown command")

    except websockets.exceptions.ConnectionClosed:
        clients.remove(websocket)

async def main():
    await asyncio.gather(
        webserver('0.0.0.0', 8000),
        websockets.serve(echo, "0.0.0.0", 8765)
        )

asyncio.run(main())


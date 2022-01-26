import asyncio
import os
import subprocess
from contextlib import contextmanager

import websockets
from dotenv import load_dotenv

load_dotenv()
TIMEOUT = int(os.getenv("TIMEOUT")) if os.getenv("TIMEOUT") else 10


@contextmanager
def file_open(path):
    try:
        yield
    finally:
        os.remove(path)


async def execution(websocket, text):
    with open("script.py", "w", encoding="utf8") as file:
        file.write(text)
        path = os.path.abspath(file.name)

    with file_open(path):
        proc = subprocess.Popen(
            ["python", "-u", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf8",
        )
        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip()
            # yield line
            await websocket.send(line)

        for line in iter(proc.stderr.readline, ""):
            line = line.rstrip()
            # yield line
            await websocket.send(line)


async def start_server(websocket):
    async for text in websocket:
        await websocket.send("got it")
        print(f">>> {text} <<<")
        try:
            await asyncio.wait_for(execution(websocket, text), timeout=TIMEOUT)
        except asyncio.TimeoutError:
            await websocket.send("TIMEOUT ! ! !")
        """async for result in execution(text):
            await websocket.send(result)"""
        await websocket.send("got it")


server = websockets.serve(start_server, "", 3000)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()

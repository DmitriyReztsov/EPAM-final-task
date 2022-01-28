import asyncio
import os
import subprocess
import sys

import websockets
from dotenv import load_dotenv

load_dotenv()
TIMEOUT = int(os.getenv("TIMEOUT")) if os.getenv("TIMEOUT") else 10


async def execution(websocket, text):
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-u", "-c", text, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    async for line in proc.stdout:
        await websocket.send(line.decode("utf8"))

    async for line in proc.stderr:
        await websocket.send(line.decode("utf8"))


async def start_server(websocket):
    async for text in websocket:
        await websocket.send("start execution")
        print(f">>> {text} <<<")
        text = (
            "import sys\n"
            "sys.modules['os'] = None\n"
            "del __builtins__.open\n"
            "del __builtins__.exec\n"
            "del __builtins__.eval\n\n" + text
        )
        try:
            await asyncio.wait_for(execution(websocket, text), timeout=TIMEOUT)
        except asyncio.TimeoutError:
            await websocket.send("TIMEOUT ! ! !")
        await websocket.send("that's all, folks")


server = websockets.serve(start_server, "", 3000)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()

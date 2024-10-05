import asyncio
import websockets
import json
import logging
from typing import Dict, Set
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)

@dataclass
class Client:
    websocket: websockets.WebSocketServerProtocol
    nickname: str
    rooms: Set[str] = field(default_factory=set)

clients: Dict[str, Client] = {}

async def handle_client(websocket: websockets.WebSocketServerProtocol, path: str):
    client = None
    try:
        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
        data = json.loads(message)
        if data['type'] == 'nickname':
            nickname = data['nickname']
            if nickname in clients:
                await websocket.send(json.dumps({"error": "Nickname already taken"}))
                return
            client = Client(websocket, nickname)
            clients[nickname] = client
            await broadcast(f"{nickname} has joined the chat!")
            logging.info(f"New client connected: {nickname}")
        else:
            await websocket.send(json.dumps({"error": "Please send your nickname first"}))
            return

        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'chat':
                if len(data['message']) > 1000:  # Limit message size
                    await websocket.send(json.dumps({"error": "Message too long"}))
                    continue
                await broadcast(data['message'], sender=nickname)
    except asyncio.TimeoutError:
        logging.warning(f"Client timed out: {client.nickname if client else 'Unknown'}")
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"Client disconnected: {client.nickname if client else 'Unknown'}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON received from client: {client.nickname if client else 'Unknown'}")
    finally:
        if client:
            del clients[client.nickname]
            await broadcast(f"{client.nickname} has left the chat!")

async def broadcast(message: str, sender: str = None, room: str = None):
    message_json = json.dumps({"sender": sender, "message": message, "room": room})
    if room:
        targets = [client for client in clients.values() if room in client.rooms]
    else:
        targets = clients.values()
    
    await asyncio.gather(
        *(client.websocket.send(message_json) for client in targets),
        return_exceptions=True
    )

async def main():
    server = await websockets.serve(handle_client, "localhost", 55555)
    logging.info("Server started on ws://localhost:55555")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
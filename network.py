import websockets
import asyncio
import json

class Network:
    def __init__(self, uri:str = "ws://localhost:8765") -> None:
        self.uri = uri
        self.conn:websockets.WebSocketClientProtocol|None = None
        self.player_num = 0
    
    async def connect(self) -> bool:
        '''Connect to the server, returns False if failed, True if successful'''
        try:
            self.conn = await websockets.connect(self.uri)
        except ConnectionRefusedError as e:
            print(e)
            return False
        return True

    async def login(self, username:str) -> dict:
        if not self.conn:
            return {}
        await self.conn.send(json.dumps({"action":"login", "username":username}))
        try:
            data = json.loads(await self.conn.recv())
        except websockets.ConnectionClosedOK as e:
            print("Login unsucessful, reason:", e.reason)
            return {}

        self.player_num = data["player_num"]
        return data
        
    async def get(self) -> dict:
        if not self.conn:
            return {}
        await self.conn.send(json.dumps({"action":"get", "player_num":self.player_num}))
        
        try:
            data = json.loads(await self.conn.recv())
        except websockets.ConnectionClosedOK as e:
            print("Get game unsucessful, reason:", e.reason)
            return {}
        
        return data
    
    async def setup_change(self, space_ids:list, piece_values:list) -> None:
        if not self.conn:
            return
        await self.conn.send(json.dumps({"action":"setup", "space_ids":space_ids, "piece_values":piece_values}))
    
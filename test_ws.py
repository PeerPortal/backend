import asyncio
import websockets

async def test_ws():
    uri = "ws://localhost:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        await websocket.send("你好，WebSocket！")
        response = await websocket.recv()
        print("收到回复:", response)

if __name__ == "__main__":
    asyncio.run(test_ws()) 
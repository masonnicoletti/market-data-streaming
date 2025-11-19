import asyncio
import websockets
import json

websocket_uri = "wss://ws-feed.exchange.coinbase.com"

async def connect():
    try:
        websocket = await websockets.connect(
            websocket_uri,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=10
        )
        print("Connected to Coinbase Websocket")

        subscribe_payload = {
        "type": "subscribe",
        "channels": [
            {"name": "ticker", "product_ids": ["BTC-USD", "ETH-USD"]},
            {"name": "level2", "product_ids": ["BTC-USD", "ETH-USD"]}
            ]
        }

        await websocket.send(json.dumps(subscribe_payload))

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                print(data)
            
            except websockets.ConnectionClosed as e:
                print(f"Connection closed: {e}")
                break
            
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    except Exception as e:
        print(f"Connection error: {e}")
        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(connect())
    except KeyboardInterrupt:
        print("\n Exited out of Streaming")
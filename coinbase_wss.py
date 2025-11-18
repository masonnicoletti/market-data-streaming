import websocket
import json

websocket_uri = "wss://ws-feed.exchange.coinbase.com"

ws = websocket.create_connection(websocket_uri)

subscribe_payload = {
    "type": "subscribe",
    "product_ids": ["BTC-USD", "ETH-USD"],
    "channels": ["ticker", "level2"]
}

ws.send(json.dumps(subscribe_payload))
print("Subscription message sent")

while True:
    message = ws.recv()
    print(message)

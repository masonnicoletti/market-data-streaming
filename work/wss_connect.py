import websocket
import json

websocket_uri = "wss://ws-feed.exchange.coinbase.com"


def coinbase_wss_connect():

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
        data = json.loads(message)
        print(data)


if __name__ == "__main__":
    coinbase_wss_connect()

import websocket
import json

API_KEY = "22C7QdK1UUcha8i_sps3LBHCrFHFgGC3"

def on_open(ws):
    print("Connected to Polygon WebSocket.")

    # Authenticate
    auth_data = {"action": "auth", "params": API_KEY}
    ws.send(json.dumps(auth_data))

    # Subscribe to SPX index updates
    sub_data = {"action": "subscribe", "params": "I:SPX"}
    ws.send(json.dumps(sub_data))
    print("Subscribed to I:SPX")

def on_message(ws, message):
    data = json.loads(message)
    print("Received:", data)

def on_close(ws):
    print("Connection closed.")

if __name__ == "__main__":
    socket_url = "wss://delayed.massive.com/stocks"
    ws = websocket.WebSocketApp(
        socket_url,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close
    )

    ws.run_forever()

import json
import time
import logging
import asyncio
import websockets
from quixstreams import Application

kafka_broker = "localhost:19092"
websocket_uri = "wss://ws-feed.exchange.coinbase.com"

async def stream_coinbase():

    app = Application(
        broker_address=kafka_broker,
        loglevel="INFO"
    )

    topic = app.topic(
        name="crypto-stream",
        value_serializer="json")
    
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
        "channels": [{"name": "ticker", "product_ids": ["BTC-USD", "ETH-USD"]}]
        }

        await websocket.send(json.dumps(subscribe_payload))
        
        with app.get_producer() as producer:

            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(data)

                    key = data['type']

                    serialized = topic.serialize(key=key, value=data)

                    producer.produce(
                        topic=topic.name,
                        key=serialized.key,
                        value=serialized.value
                    )
                    print("Produced a message to Kafka")
                
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
        asyncio.run(stream_coinbase())
    except KeyboardInterrupt:
        print("\n Exited out of Streaming")
import json
import time
import logging
import asyncio
import websockets
from quixstreams import Application


kafka_broker = "localhost:19092"
websocket_uri = "wss://ws-feed.exchange.coinbase.com"


logging.basicConfig(
    filename='../logs/coinbase_producer.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)
logger = logging.getLogger(__name__)


async def stream_coinbase():

    # Define entry point for Kafka connection
    app = Application(
        broker_address=kafka_broker,
        loglevel="INFO"
    )
    logger.info("Initialized Kafka connection")

    # Create Kafka topic
    topic = app.topic(
        name="crypto-stream",
        value_serializer="json")
    logger.info("Connected to Kafka topic")

    # Create buffer and exit condition for retries
    retries = 0
    while retries < 10:

        try:
            # Connect to Coinbase websocket
            websocket = await websockets.connect(
                websocket_uri,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=30
            )
            logger.info("Connected to Coinbase websocket")

            # Define channels to listen to over websocket
            subscribe_payload = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": ["BTC-USD", "ETH-USD", "SOL-USD"]}]
            }

            # Send data over websocket connection
            await websocket.send(json.dumps(subscribe_payload)) 
            
            with app.get_producer() as producer:
                logger.info("Start streaming from Coinbase websocket")

                message_count = 0

                while True:

                    try:
                        # Receive messages from websocket
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(data)

                        key = data['type']

                        # Encode messages for publication to Kafka
                        serialized = topic.serialize(key=key, value=data)

                        # Send messages to Kafka
                        producer.produce(
                            topic=topic.name,
                            key=serialized.key,
                            value=serialized.value
                        )

                        message_count += 1

                        if message_count % 1000 == 0:
                            logger.info(f"Produced {message_count} messages to Kafka")
                    
                    # Exception for closed Kafka connection
                    except websockets.ConnectionClosed as e:
                        retries += 1
                        print(f"Connection closed: {e}")
                        logger.error(f"Connection closed: {e}")
                        await asyncio.sleep(5)
                        break
                    
                    # Exception for other errors
                    except Exception as e:
                        retries += 1
                        print(f"Error: {e}")
                        logger.error(f"Error: {e}")
                        await asyncio.sleep(5)
                        break
    
        except Exception as e:
            print(f"Connection error: {e}")
            logger.error(f"Connection error: {e}")
            await asyncio.sleep(60)
        
    print("Maximum retries exceeded. Exited out of streaming")
    logger.info("Maximum retries exceeded. Exited out of streaming")



if __name__ == "__main__":
    try:
        asyncio.run(stream_coinbase())
    except KeyboardInterrupt:
        print("\n Exited out of Streaming")
        logger.info("Exited out of Streaming")

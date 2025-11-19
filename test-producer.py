import json
import time
import logging
from quixstreams import Application

KAFKA_BROKER = "localhost:19092"
TOPIC = "test-crypto-stream"

def main():
    app = Application(
        broker_address=KAFKA_BROKER,
        loglevel="DEBUG"
    )

    topic = app.topic(TOPIC)

    with app.get_producer() as producer:
        while True:
            producer.produce(
                topic=TOPIC,
                key="BTC-USD",
                value=json.dumps({"date": time.time(), "price": "100000"})
            )
            print("Produced a message to Kafka")
            time.sleep(5)


if __name__ == "__main__":
    main()

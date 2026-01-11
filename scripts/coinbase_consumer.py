import os
import json
import time
import logging
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import timedelta, datetime
from quixstreams import Application


kafka_broker = "localhost:19092"


logging.basicConfig(
    filename='../logs/coinbase_consumer.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)
logger = logging.getLogger(__name__)


def set_window(record_time):

    # Determine the start and end of an hour window
    window_start = record_time.replace(minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(hours=1)

    return window_start, window_end



def parse_data(key, value, record_time):

    # Parse message fields and store as a dictionary
    entry = {
        "type": key,
        "sequence": value.get("sequence"),
        "product_id": value.get("product_id"),
        "price": value.get("price"),
        "open_24h": value.get("open_24h"),
        "volume_24h": value.get("volume_24h"),
        "low_24h": value.get("low_24h"),
        "high_24h": value.get("high_24h"),
        "volume_30d": value.get("volume_30d"),
        "best_bid": value.get("best_bid"),
        "best_bid_size": value.get("best_bid_size"),
        "best_ask": value.get("best_ask"),
        "best_ask_size": value.get("best_ask_size"),
        "side": value.get("side"),
        "time": record_time,
        "trade_id": value.get("trade_id"),
        "last_size": value.get("last_size") 
    }

    return entry



def write_parquet(data, window_start):

    # Convert message data into a parquet table
    df = pd.DataFrame(data)
    table = pa.Table.from_pandas(df)

    # Write filename based on window time
    timestamp = window_start.strftime("%Y-%m-%d_%H")
    filename = f"../data/coinbase_{timestamp}.parquet"
    
    # Append new data to parquet file if already exists
    if os.path.exists(filename):
        existing_table = pq.read_table(filename)
        new_table = pa.concat_tables([existing_table, table])
        pq.write_table(new_table, filename)
    
    # Write to new parquet file
    else:
        pq.write_table(table, filename)



def consume_coinbase():

    # Define entry point for Kafka consumer connection
    app = Application(
        broker_address=kafka_broker,
        loglevel="INFO",
        consumer_group="coinbase-consumer",
        auto_offset_reset="earliest"
    )
    logger.info("Initialized Kafka connection")

    buffer = []
    window_start = None

    with app.get_consumer() as consumer:

        # Subscribe to Kafka topic
        consumer.subscribe(['crypto-stream'])
        logger.info("Connected to Kafka topic")

        try:
            while True:
                # Setup polling to wait for messages
                message = consumer.poll(5)
                
                if message is None:
                    print("Waiting for message")
                    logger.info("Waiting for message")
                
                elif message.error() is not None:
                    raise Exception(message.error())
                
                else:
                    # Decode message from Kafka
                    key = message.key().decode("utf-8")
                    value = json.loads(message.value())
                    offset = message.offset()

                    # Confirm the correct message type
                    if key != "ticker":
                        continue

                    # Extract record time
                    time_string = value.get("time")
                    record_time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ")

                    # Define initial window
                    if window_start is None:
                        window_start, window_end = set_window(record_time)
                        logger.info(f"Recording window from: {window_start} - {window_end}")

                    # Write data to parquet file if window is over
                    if record_time >= window_end:
                        write_parquet(buffer, window_start)
                        logger.info(f"Finished recording to coinbase_{window_start} file")
                        buffer.clear()
                        window_start, window_end = set_window(record_time)
                        logger.info(f"Recording window from: {window_start} - {window_end}")
                    
                    # Parse new message and store in memory
                    entry = parse_data(key, value, record_time)
                    buffer.append(entry)

                    # Print outputs to screen
                    print(f"Key: {key}")
                    print(f"Value: {value}")
                    print(f"Record time: {record_time}")
                    print(f"Offset: {offset}")

                    if offset % 1000 == 0:
                        logger.info(f"Recorded {offset} messages")
                    
                    # Track message offset
                    consumer.store_offsets(message)
        
        # Allow for graceful exit from consumer
        except KeyboardInterrupt:
            write_parquet(buffer, window_start)
            logger.info(f"Finished recording to coinbase_{window_start} file")
            print("\nExited Kafka consumer")
            logger.info("Exited Kafka consumer")
        
        # Close Kafka connection
        finally:
            consumer.close()


if __name__ == "__main__":
    consume_coinbase()

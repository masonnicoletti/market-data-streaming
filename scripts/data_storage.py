import os
import duckdb
import logging


logging.basicConfig(
    filename='../logs/data_storage.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)


def extract_parquet_files():

    # Extract locally saved parquet files from the data folder
    files = os.listdir('../data/')
    parquet_files = [file for file in files if file.endswith('.parquet')]

    return parquet_files


def data_storage():

    con = None

    try:
        # Establish DuckDB connection
        con = duckdb.connect(database='../coinbase.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

        # Create table schema
        con.execute(f"""
            CREATE OR REPLACE TABLE coinbase_ticker (
                type VARCHAR,
                sequence BIGINT,
                product_id VARCHAR,
                price DOUBLE,
                open_24h DOUBLE,
                volume_24h DOUBLE,
                low_24h DOUBLE,
                high_24h DOUBLE,
                volume_30d DOUBLE,
                best_bid DOUBLE,
                best_bid_size DOUBLE,
                best_ask DOUBLE,
                best_ask_size DOUBLE,
                side VARCHAR,
                time TIMESTAMP,
                trade_id BIGINT,
                last_size DOUBLE,
            );
        """)
        logger.info("Created coinbase_ticker table")

        # Loop through parquet files
        parquet_files = extract_parquet_files()
        for file in parquet_files:

            file_path = f"../data/{file}"
            
            # Insert data into table
            con.execute(f"""
                INSERT INTO coinbase_ticker
                SELECT * FROM read_parquet('{file_path}')
                ORDER BY time;
            """)
            logger.info(f"Imported {file.strip('.parquet')} data to DuckDB")

        # Close DuckDB connection
        con.close()
        logger.info("Closed DuckDB connection")


    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")



if __name__ == "__main__":
    data_storage()

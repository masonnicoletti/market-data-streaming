import duckdb
import logging
import pandas as pd


logging.basicConfig(
    filename='../logs/data_analytics.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)


def data_analytics():

    con = None

    try:
        # Connect to DuckDB instance
        con = duckdb.connect(database='../coinbase.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")


        # Create a table for Bitcoin transactions
        con.execute("""
            CREATE OR REPLACE TABLE bitcoin AS
            SELECT trade_id, price, side, time
            FROM coinbase_ticker
            WHERE product_id = 'BTC-USD';
        """)
        logger.info("Created Bitcoin table")


        # Create a table for Ethereum transactions
        con.execute("""
            CREATE OR REPLACE TABLE ethereum AS
            SELECT trade_id, price, side, time
            FROM coinbase_ticker
            WHERE product_id = 'ETH-USD';
        """)
        logger.info("Created Ethereum table")


        # Create a table for Solana transactions
        con.execute("""
            CREATE OR REPLACE TABLE solana AS
            SELECT trade_id, price, side, time
            FROM coinbase_ticker
            WHERE product_id = 'SOL-USD';
        """)
        logger.info("Created Solana table")


        # Create a summary table for products
        con.execute("""
            CREATE OR REPLACE TABLE product_summary AS
            SELECT
                product_id, 
                AVG(price) AS avg_price,
                MAX(price) AS max_price,
                MIN(price) AS min_price,
                AVG(volume_24h) AS avg_daily_volume,
                AVG(open_24h) AS avg_open,
                AVG(low_24h) AS avg_daily_low,
                AVG(high_24h) AS avg_daily_high,
                AVG(best_bid) AS avg_best_bid,
                AVG(best_ask) AS avg_best_ask,
                AVG(last_size) AS avg_last_size,
                SUM(side = 'buy') AS total_buys,
                SUM(side = 'sell') AS total_sells,
                total_buys/total_sells AS buy_to_sell_ratio
            FROM coinbase_ticker
            GROUP BY product_id
            ORDER BY avg_price DESC;
        """)
        logger.info("Created product summary table")


        # Create a table for daily summaries
        con.execute("""
            CREATE OR REPLACE TABLE daily_summary AS
            SELECT
                DATE(time) AS date,
                product_id,
                AVG(price) AS avg_price,
                MAX(price) AS max_price,
                MIN(price) AS min_price,
                SUM(side = 'buy') AS total_buys,
                SUM(side = 'sell') AS total_sells,
                (total_buys + total_sells) AS volume,
                total_buys/total_sells AS buy_to_sell_ratio
            FROM coinbase_ticker
            GROUP BY date, product_id
            ORDER BY date, product_id;
        """)
        logger.info("Created daily summary table")


        # Create a table for temporal analysis
        con.execute("""
            CREATE OR REPLACE TABLE temporal_analysis AS
            SELECT
                DATE(time) AS date, 
                product_id,
                price, 
                side, 
                HOUR(time) AS hour,
                DAYOFWEEK(time) AS day_number,
                CASE DAYOFWEEK(time)
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                    WHEN 7 THEN 'Sunday'
                END AS day_of_week
            FROM coinbase_ticker;
        """)
        logger.info("Created temporal table")
        

        # Close DuckDB connection
        con.close()
        logger.info("Closed DuckDB connection")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")



if __name__ == "__main__":
    data_analytics()

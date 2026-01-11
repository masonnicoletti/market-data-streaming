import logging
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

logging.basicConfig(
    filename='../logs/data_visualizations.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)


def produce_plots():
    
    con = None

    try:
        # Connect to DuckDB instance
        con = duckdb.connect(database='../coinbase.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")


        # Extract and plot Bitcoin price over time
        bitcoin_timeseries = con.execute("""
            SELECT price, time FROM bitcoin
            ORDER BY time;
        """).df()

        plt.plot(bitcoin_timeseries['time'], bitcoin_timeseries['price'], color='#f7931a')
        plt.title("Bitcoin Ticker Timeseries")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.savefig("../plots/bitcoin_timeseries.png")
        plt.close()
        logger.info("Produced Bitcoin timeseries plot")

        # Extract and plot Ethereum price over time
        ethereum_timeseries = con.execute("""
            SELECT price, time FROM ethereum
            ORDER BY time;
        """).df()

        plt.plot(ethereum_timeseries['time'], ethereum_timeseries['price'], color='#4043AE')
        plt.title("Ethereum Ticker Timeseries")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.savefig("../plots/ethereum_timeseries.png")
        plt.close()
        logger.info("Produced Ethereum timeseries plot")


        # Extract and plot Solana price over time
        solana_timeseries = con.execute("""
            SELECT price, time FROM solana
            ORDER BY time;
        """).df()

        plt.plot(solana_timeseries['time'], solana_timeseries['price'], color='#14F195')
        plt.title("Solana Ticker Timeseries")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.savefig("../plots/solana_timeseries.png")
        plt.close()
        logger.info("Produced Solana timeseries plot")


        # Plot timeseries of all product prices
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        sns.lineplot(data=bitcoin_timeseries, x='time', y='price', ax=ax1, color='#f7931a', label='Bitcoin', estimator=None)
        sns.lineplot(data=ethereum_timeseries, x='time', y='price', ax=ax2, color='#4043AE', label='Ethereum', estimator=None)
        sns.lineplot(data=solana_timeseries, x='time', y='price', ax=ax3, color='#14F195', label='Solana', estimator=None)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Bitcoin", color='#f7931a')
        ax2.set_ylabel("Ethereum", color='#4043AE')
        ax3.set_ylabel("Solana", color='#14F195')
        ax1.tick_params(axis='y', labelcolor='#f7931a')
        ax2.tick_params(axis='y', labelcolor='#4043AE')
        ax3.tick_params(axis='y', labelcolor='#14F195')
        plt.title("Coinbase Product Timeseries")
        plt.legend()
        fig.tight_layout()
        plt.savefig("../plots/coinbase_timeseries.png")
        plt.close()
        logger.info("Produced Coinbase product timeseries")


        # Extract and plot transactions through the week
        trades_by_day = con.execute("""
            SELECT day_number, COUNT(day_number)
            FROM temporal_analysis
            GROUP BY day_number;
        """).df()
        day_of_week_dict = {0: "Sun", 1: "Mon", 2: "Tues", 3: "Wed", 4: "Thurs", 5: "Fri", 6: "Sat"}
        trades_by_day['day_number'] = trades_by_day['day_number'].replace(day_of_week_dict)
        trades_by_day.columns = ['day_of_week', 'num_trades']
        trades_by_day['num_trades'] = trades_by_day['num_trades'] / 1000
        
        sns.barplot(data=trades_by_day, x='day_of_week', y='num_trades', color="indigo")
        plt.title("Coinbase Trades by Day")
        plt.xlabel("Day of Week")
        plt.ylabel("Number of Trades (1000)")
        plt.savefig("../plots/daily_volume.png")
        plt.close()
        logger.info("Produced daily volume plot")


        # Extract and plot buy-to-sell ratio as timeseries per product
        product_dict = {"bitcoin": "BTC-USD", "ethereum": "ETH-USD", "solana": "SOL-USD"}
        buy_sell_timeseries = {}
        for product, symbol in product_dict.items():
            buy_sell_timeseries[product] = con.execute(f"""
                SELECT date, product_id, buy_to_sell_ratio FROM daily_summary
                WHERE product_id = '{symbol}'
                ORDER BY date, product_id;
            """).df()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=buy_sell_timeseries['bitcoin'], x='date', y='buy_to_sell_ratio',
                    color='#f7931a', linewidth=3, marker='o', label='Bitcoin', estimator=None)
        sns.lineplot(data=buy_sell_timeseries['ethereum'], x='date', y='buy_to_sell_ratio', 
                    color='#4043AE', linewidth=3, marker='o', label='Ethereum', estimator=None)
        sns.lineplot(data=buy_sell_timeseries['solana'], x='date', y='buy_to_sell_ratio', 
                    color='#14F195', linewidth=3, marker='o', label='Solana', estimator=None)
        ax.axhline(y=1, color='grey', linestyle='--')
        ax.axhspan(ax.get_ylim()[0], 1, facecolor='red', alpha=0.1)
        ax.axhspan(1, ax.get_ylim()[1], facecolor='green', alpha=0.1)
        plt.xlabel("Date")
        plt.ylabel("Product")
        plt.title("Coinbase Product Timeseries")
        plt.xticks(rotation=45)
        plt.legend(title="Buy-to-Sell Ratio")
        fig.tight_layout()
        plt.savefig("../plots/product_buy_to_sell.png")
        plt.close()
        logger.info("Produced buy-to-sell timeseries per product")


        # Extract and plot average total transactions per hour
        hourly_transactions = con.execute("""
            WITH daily_trades AS(
                SELECT date, hour, COUNT(side) as total_trades
                FROM temporal_analysis
                GROUP BY date, hour
            )
            SELECT hour, AVG(total_trades) AS avg_hourly_volume
            FROM daily_trades
            GROUP BY hour
            ORDER BY hour;
        """).df()

        sns.barplot(hourly_transactions, x='hour', y='avg_hourly_volume', color='navy')
        plt.title("Average Hourly Volume on Coinbase")
        plt.xlabel("Hour of the Day")
        plt.ylabel("Average Transactions")
        plt.tight_layout()
        plt.savefig("../plots/hourly_volume.png")
        plt.close()
        logger.info("Produced average hourly volume plot")


        # Extract and plot distribution of Coinbase products
        product_ratio = con.execute("""
            SELECT product_id, COUNT(product_id) as total_trades
            FROM coinbase_ticker
            GROUP BY product_id;
        """).df()

        plt.pie(product_ratio['total_trades'], labels=product_ratio['product_id'])
        plt.title("Distribution of Coinbase Product Transactions")
        plt.savefig("../plots/product_distribution.png")
        plt.close()
        logger.info("Produce product distribution plot")

        
        # Close DuckDB connection
        con.close()
        logger.info("Closed DuckDB connection")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")



if __name__ == "__main__":
    produce_plots()
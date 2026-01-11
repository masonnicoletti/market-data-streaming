import time
import logging
import duckdb
import pandas as pd
import seaborn as sns
from datetime import date
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output

logging.basicConfig(
    filename='../logs/daily_dashboard.log',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)
logger = logging.getLogger(__name__)


def produce_daily_dash():

    con = None

    try:
        # Connect to DuckDB instance
        con = duckdb.connect(database='../coinbase.duckdb', read_only=False)
        logger.info("Connected to DuckDB instance")

        # Determine today's date
        current_date = date.today().strftime('%Y-%m-%d')

        # Extract coinbase data from today
        daily_summary_df = con.execute(f"""
            SELECT * FROM coinbase_ticker
            WHERE DATE(time) = DATE('{current_date}')
            ORDER BY time;
        """).df()
        logger.info("Extracted daily Coinbase data")

        # Close DuckDB connection
        con.close()
        logger.info("Closed DuckDB connection")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
        return None
    
    return daily_summary_df



# Store df of daily transactions
daily_summary_df = produce_daily_dash()



app = Dash()
logger.info("Started Plotly dashboard")

app.layout = html.Div(
    style={
        'backgroundColor':'lightblue',
        'padding': '20px',
        'borderRadius': '5px',
        'marginBottom': '25px'},
    children=[
        
        html.H1(
            "Daily Coinbase Dashboard", 
            style={
                'color': 'darkblue',
                'textAlign': 'center'}
            ),

        html.Div(
            style={'display':'flex'},
            children=[
                html.Div(
                    "Select Product",
                    style={'color': 'darkblue', 'fontWeight':'bold'}),
                
                dcc.Dropdown(
                    id='coinbase-product',
                    options=[
                        {'label': 'Bitcoin', 'value': 'BTC-USD'},
                        {'label': 'Ethereum', 'value': 'ETH-USD'},
                        {'label': 'Solana', 'value': 'SOL-USD'}
                    ],
                    value='BTC-USD', 
                    multi=True,
                    style={'color':'purple'}
                )
            ]
        ),

        dcc.Graph(id='price-timeseries'),

        dcc.Graph(id='hourly-volume')

    ]
)


@app.callback(
    Output('price-timeseries', 'figure'),
    Input('coinbase-product', 'value')
)

def update_price_timeseries(selected_products):

    if isinstance(selected_products, str):
        selected_products = [selected_products]

    filtered_df = daily_summary_df[daily_summary_df['product_id'].isin(selected_products)]
    
    # Create a multi-series line plot
    fig = px.line(filtered_df, x='time', y='price', 
        color='product_id', title='Daily Price Timeseries'
    )

    return fig


@app.callback(
    Output('hourly-volume', 'figure'),
    Input('coinbase-product', 'value')
)

def update_hourly_volume(selected_products):
    
    if isinstance(selected_products, str):
        selected_products = [selected_products]

    filtered_df = daily_summary_df[daily_summary_df['product_id'].isin(selected_products)].copy()

    filtered_df.loc[:, "hour"] = filtered_df["time"].dt.floor("h")

    grouped_df = (
        filtered_df.groupby(["hour", "product_id"]).size().reset_index(name="trades")
    )

    fig = px.bar(grouped_df, x='hour', y='trades', 
        color='product_id', barmode='stack', title='Hourly Volume')
    
    return fig




if __name__ == "__main__":
    app.run(debug=False)
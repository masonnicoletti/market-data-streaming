# coinbase-streaming

### DS 3022 
Data Project 3

**Objective:** Stream live Coinbase data and perform analysis on the findings.


#### Coinbase Websocket Documentation
**Link:** https://docs.cdp.coinbase.com/exchange/websocket-feed/overview


### Steps:
1) Start a docker instance\
        `docker compose up -d`
2) Create a virtual environment and install requirements\
        `pipenv shell` or `python3 -m venv .venv` `source .venv/bin/activate`\
        `pip install -r requirements.txt`
3) Navigate into the scripts folder\
        `cd scripts`
4) Stream from the Coinbase websocket and run the Kafka producer\
        run `coinbase_producer.py`
5) Run the Kafka consumer and save data locally\
        run `coinbase_consumer.py`
6) Store the data for analysis\
        run `data_storage.py`\
        run `data_analytics.py`
7) Create visualizations and start a dashboard\
        run `data_visualizations.py`\
        run `daily_dashboard.py`

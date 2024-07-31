import requests
import mysql.connector
import pandas as pd
import json


def fetch_and_process_response(url, company_name):
    response = requests.get(url)
    data = response.json()
    price_data = data['price_data']

    df = pd.DataFrame({
        'timestamp': [item for item in price_data['timestamp']],
        'opening_price': [item for item in price_data['open']],
        'closing_price': [item for item in price_data['close']],
    })

    df['ticker_symbol'] = data['ticker']
    df['company_name'] = 'Tesla Inc.'
    df['current_price'] = df['closing_price'] 
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    latest_data = df.loc[df['timestamp'].idxmax()]
    print(latest_data)
    return latest_data

urls = {
    "TSLA": "https://c4rm9elh30.execute-api.us-east-1.amazonaws.com/default/cachedPriceData?ticker=TSLA",
    "C": "https://c4rm9elh30.execute-api.us-east-1.amazonaws.com/default/cachedPriceData?ticker=C",
    "AMZN": "https://c4rm9elh30.execute-api.us-east-1.amazonaws.com/default/cachedPriceData?ticker=AMZN",
    "AAPL": "https://c4rm9elh30.execute-api.us-east-1.amazonaws.com/default/cachedPriceData?ticker=AAPL"
}

company_names = {
    "TSLA": "Tesla Inc.",
    "C": "Citigroup Inc.",
    "AMZN": "Amazon Inc.",
    "AAPL": "Apple Inc."
}

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="c0nygre",
    database="portfolio_manager"
)

mycursor = mydb.cursor()

mycursor.execute("""
CREATE TABLE IF NOT EXISTS stocks (
    ticker_symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    price_timestamp TIMESTAMP NOT NULL,
    opening_price DECIMAL(10, 2) NOT NULL,
    closing_price DECIMAL(10, 2) NOT NULL
)
""")

for ticker, url in urls.items():
    latest_data = fetch_and_process_response(url, company_names[ticker])

    sql = """
    INSERT INTO stocks (ticker_symbol, company_name, current_price, price_timestamp, opening_price, closing_price)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        company_name=VALUES(company_name),
        current_price=VALUES(current_price),
        price_timestamp=VALUES(price_timestamp),
        opening_price=VALUES(opening_price),
        closing_price=VALUES(closing_price)
    """
    val = (
        latest_data['ticker_symbol'], latest_data['company_name'], latest_data['current_price'], 
        latest_data['timestamp'], latest_data['opening_price'], latest_data['closing_price']
    )
    mycursor.execute(sql, val)
    
mydb.commit()
print(mycursor.rowcount, "records inserted or updated.")

mycursor.close()
mydb.close()

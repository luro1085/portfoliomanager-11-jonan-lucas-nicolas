from flask import Flask, jsonify
import mysql.connector
import requests
import pandas as pd

app = Flask(__name__)

# MySQL Connection Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'c0nygre',
    'database': 'portfolio_manager' 
}

# Function to fetch and process data from API
def fetch_and_process_response(url, company_name):
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Example of how to process the data
        price_data = data.get('price_data', {})
        
        df = pd.DataFrame({
            'timestamp': price_data.get('timestamp', []),
            'opening_price': price_data.get('open', []),
            'closing_price': price_data.get('close', [])
        })
        
        df['ticker_symbol'] = data.get('ticker', '')
        df['company_name'] = company_name
        df['current_price'] = df['closing_price']  # Example, adjust as needed
        df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convert timestamp to datetime
        
        latest_data = df.loc[df['timestamp'].idxmax()]  # Get the latest data based on timestamp
        
        return latest_data
    else:
        print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return None

# Flask route to populate database
@app.route('/populate_db')
def populate_database():
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

    mydb = mysql.connector.connect(**db_config)
    mycursor = mydb.cursor()

    # Ensure the table exists or create it
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

    # Populate the database
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
    mycursor.close()
    mydb.close()

    return jsonify({"message": "Database populated successfully"})

if __name__ == '__main__':
    app.run(debug=True)

import mysql.connector

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

mycursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_type VARCHAR(50) NOT NULL,
    ticker_symbol VARCHAR(10),
    company_name VARCHAR(100) NOT NULL,
    purchase_cost DECIMAL(10, 2),
    sale_revenue DECIMAL(10, 2),
    quantity INT,
    purchase_price_per_share DECIMAL(10, 2),
    sell_price_per_share DECIMAL(10, 2),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker_symbol) REFERENCES stocks(ticker_symbol)
)
""")

mycursor.execute("""
CREATE TABLE IF NOT EXISTS assets (
    asset_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_type VARCHAR(50) NOT NULL,
    ticker_symbol VARCHAR(10),
    company_name VARCHAR(100) NOT NULL,
    total_shares_owned INT NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    last_updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker_symbol) REFERENCES stocks(ticker_symbol)
)
""")


print("Tables created successfully.")

mycursor.close()
mydb.close()


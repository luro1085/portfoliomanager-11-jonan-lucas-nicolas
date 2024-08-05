import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="c0nygre",
    database="portfolio_manager"
)

mycursor = mydb.cursor()

mycursor.execute("DROP TABLE IF EXISTS transactions")
mycursor.execute("DROP TABLE IF EXISTS assets")
#mycursor.execute("DROP TABLE IF EXISTS stocks")


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
    purchase_price DECIMAL(10, 2),
    sell_price DECIMAL(10, 2),
    transaction_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    portfolio_value_before DECIMAL(10, 2) NOT NULL,
    portfolio_value_after DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (ticker_symbol) REFERENCES stocks(ticker_symbol)
)
""")

mycursor.execute("""
CREATE TABLE IF NOT EXISTS assets (
    asset_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_type VARCHAR(50) NOT NULL,
    ticker_symbol VARCHAR(10),
    company_name VARCHAR(100) NOT NULL,
    total_quantity INT NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    current_total_market_value DECIMAL(10, 2) NOT NULL,
    total_value_change_from_cost DECIMAL(10, 2) NOT NULL,
    percentage_value_change_from_cost DECIMAL(10, 2) NOT NULL,
    last_updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ticker_symbol) REFERENCES stocks(ticker_symbol)
)
""")


print("Tables created successfully.")

mycursor.close()
mydb.close()


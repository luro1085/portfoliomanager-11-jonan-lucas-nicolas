import requests
import mysql.connector
import pandas as pd
import json
from datetime import datetime

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="c0nygre",
    database="portfolio_manager"
)

mycursor = mydb.cursor()

mycursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    transaction_type VARCHAR(50) NOT NULL
    ticker_symbol VARCHAR(10),
    amount DECIMAL(10, 2),
    quantity INT,
    purchase_price DECIMAL(10, 2),
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ticker_symbol REFERENCES Stocks(ticker_symbol), 
)   
""")

sample_transaction = [(1, 'buy', 'TSLA', None, 5)]

import mysql.connector
import pandas as pd

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="c0nygre",
    database="portfolio_manager"
)

mycursor = mydb.cursor()

query = "SELECT * FROM stocks"
mycursor.execute(query)
rows = mycursor.fetchall()
column_names = [i[0] for i in mycursor.description]

df = pd.DataFrame(rows, columns=column_names).set_index("ticker_symbol")

print(df)

mycursor.close()
mydb.close()

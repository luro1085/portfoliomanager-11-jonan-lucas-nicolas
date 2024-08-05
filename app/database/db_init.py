import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="c0nygre"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS portfolio_manager")

mycursor.close()
mydb.close()


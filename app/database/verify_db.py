import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="c0nygre"
)
print("Connection to MySQL server established")

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

databases = mycursor.fetchall()

for db in databases:
    print(db)


mycursor.close()
mydb.close()
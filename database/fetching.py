import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jhansi",
    database="customerss"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM customerss")

records = mycursor.fetchall()

for row in records:
    print(row)


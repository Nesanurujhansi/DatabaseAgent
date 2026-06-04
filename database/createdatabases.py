import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jhansi"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE customerss")

print("Database created successfully")
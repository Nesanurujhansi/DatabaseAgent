import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jhansi",
    database="customerss"
)

mycursor = mydb.cursor()

mycursor.execute("""
CREATE TABLE customerss (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(15),
    city VARCHAR(50),
    product_name VARCHAR(100),
    category VARCHAR(50),
    quantity INT,
    price DECIMAL(10,2)
)
""")

print("Table created successfully")
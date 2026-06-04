import mysql.connector

# Connect to MySQL server using the existing database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jhansi",
    database="customerss"
)

mycursor = mydb.cursor()

# -------------------------------------------------------
# Table 1: customers
# Stores unique customer information
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    city VARCHAR(50)
)
""")
print("Table 'customers' created successfully")

# -------------------------------------------------------
# Table 2: products
# Stores unique product and pricing information
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL
)
""")
print("Table 'products' created successfully")

# -------------------------------------------------------
# Table 3: orders
# Links customers to products with quantity and date
# Foreign keys reference customers and products tables
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
""")
print("Table 'orders' created successfully")

mydb.close()
print("\nAll normalized tables created successfully!")

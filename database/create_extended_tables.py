import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MySQL server using the existing database
mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "jhansi"),
    database=os.getenv("DB_NAME", "customerss"),
    port=os.getenv("DB_PORT", "3306")
)

mycursor = mydb.cursor()

# -------------------------------------------------------
# Table 4: stores
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS stores (
    store_id INT AUTO_INCREMENT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL
)
""")
print("Table 'stores' created successfully")

# -------------------------------------------------------
# Table 5: employees
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(50),
    salary DECIMAL(10, 2),
    store_id INT,
    FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE SET NULL
)
""")
print("Table 'employees' created successfully")

# -------------------------------------------------------
# Table 6: reviews
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
)
""")
print("Table 'reviews' created successfully")

mydb.close()
print("\nExtended tables (stores, employees, reviews) created successfully!")

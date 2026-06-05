import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MySQL server
mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "jhansi"),
    database=os.getenv("DB_NAME", "customerss"),
    port=os.getenv("DB_PORT", "3306")
)

mycursor = mydb.cursor()

# -------------------------------------------------------
# Table 7: suppliers
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100),
    country VARCHAR(50)
)
""")
print("Table 'suppliers' created successfully")

# -------------------------------------------------------
# Table 8: inventory
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    supplier_id INT,
    stock_quantity INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL DEFAULT 10,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
)
""")
print("Table 'inventory' created successfully")

# -------------------------------------------------------
# Table 9: shipments
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    shipment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_status VARCHAR(50) DEFAULT 'Pending',
    carrier VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
)
""")
print("Table 'shipments' created successfully")

# -------------------------------------------------------
# Table 10: payments
# -------------------------------------------------------
mycursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method VARCHAR(50),
    amount_paid DECIMAL(10, 2) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'Completed',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
)
""")
print("Table 'payments' created successfully")

mydb.close()
print("\nLogistics and Supply Chain tables created successfully!")

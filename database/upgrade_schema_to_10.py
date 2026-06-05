import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MySQL server
db_name = os.getenv("DB_NAME", "customerss")
print(f"Connecting to database '{db_name}'...")
mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "jhansi"),
    database=db_name,
    port=os.getenv("DB_PORT", "3306")
)

mycursor = mydb.cursor()

# -------------------------------------------------------
# Table 11: promotions
# -------------------------------------------------------
print("Creating 'promotions' table...")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS promotions (
    promotion_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percentage DECIMAL(5, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
)
""")
print("Table 'promotions' created successfully.")

# -------------------------------------------------------
# Table 12: returns
# -------------------------------------------------------
print("Creating 'returns' table...")
mycursor.execute("""
CREATE TABLE IF NOT EXISTS returns (
    return_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Processing',
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
)
""")
print("Table 'returns' created successfully.")

# -------------------------------------------------------
# Alter orders Table to include promotion_id
# -------------------------------------------------------
print("Checking and altering 'orders' table to add 'promotion_id'...")
# Check if promotion_id column already exists
mycursor.execute("""
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'orders' AND COLUMN_NAME = 'promotion_id'
""", (db_name,))

if mycursor.fetchone() is None:
    print("Adding 'promotion_id' column to 'orders' table...")
    mycursor.execute("""
    ALTER TABLE orders 
    ADD COLUMN promotion_id INT DEFAULT NULL,
    ADD CONSTRAINT fk_orders_promotions FOREIGN KEY (promotion_id) REFERENCES promotions(promotion_id) ON DELETE SET NULL
    """)
    print("'promotion_id' column and foreign key constraint added successfully.")
else:
    print("'promotion_id' column already exists in 'orders' table.")

# -------------------------------------------------------
# Add Performance Indexes
# -------------------------------------------------------
print("Adding performance indexes...")

def add_index_if_not_exists(table_name, index_name, columns_str):
    mycursor.execute("""
    SELECT INDEX_NAME 
    FROM INFORMATION_SCHEMA.STATISTICS 
    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND INDEX_NAME = %s
    """, (db_name, table_name, index_name))
    
    if mycursor.fetchone() is None:
        print(f"Creating index '{index_name}' on table '{table_name}'({columns_str})...")
        mycursor.execute(f"CREATE INDEX {index_name} ON {table_name}({columns_str})")
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists on table '{table_name}'.")

# Add indexes on date/timestamp columns
add_index_if_not_exists("orders", "idx_orders_order_date", "order_date")
add_index_if_not_exists("payments", "idx_payments_payment_date", "payment_date")
add_index_if_not_exists("shipments", "idx_shipments_shipment_date", "shipment_date")

# Explicit indexes on foreign keys (promotions in orders)
add_index_if_not_exists("orders", "idx_orders_promotion_id", "promotion_id")

mydb.commit()
mycursor.close()
mydb.close()
print("\nSchema upgrade to 10/10 completed successfully!")

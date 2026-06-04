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
# Step 1: Populate 'customers' table from the original 'customerss' table
# Extract unique customers based on name and email
# -------------------------------------------------------
mycursor.execute("""
INSERT IGNORE INTO customers (customer_name, email, phone, city)
SELECT DISTINCT customer_name, email, phone, city
FROM customerss
""")
mydb.commit()
print(f"{mycursor.rowcount} records inserted into 'customers' table")

# -------------------------------------------------------
# Step 2: Populate 'products' table from the original 'customerss' table
# Extract unique products based on product_name
# -------------------------------------------------------
mycursor.execute("""
INSERT IGNORE INTO products (product_name, category, price)
SELECT DISTINCT product_name, category, price
FROM customerss
""")
mydb.commit()
print(f"{mycursor.rowcount} records inserted into 'products' table")

# -------------------------------------------------------
# Step 3: Populate 'orders' table by joining original data
# with new customer and product IDs
# -------------------------------------------------------
mycursor.execute("""
INSERT INTO orders (customer_id, product_id, quantity)
SELECT c.customer_id, p.product_id, cs.quantity
FROM customerss cs
JOIN customers c ON cs.customer_name = c.customer_name AND cs.email = c.email
JOIN products p ON cs.product_name = p.product_name AND cs.price = p.price
""")
mydb.commit()
print(f"{mycursor.rowcount} records inserted into 'orders' table")

# -------------------------------------------------------
# Verification: Print row counts for all new tables
# -------------------------------------------------------
for table in ['customers', 'products', 'orders']:
    mycursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = mycursor.fetchone()[0]
    print(f"  '{table}' table has {count} rows")

mydb.close()
print("\nData migration completed successfully!")

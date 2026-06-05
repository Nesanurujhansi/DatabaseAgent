import mysql.connector
import os
import random
from dotenv import load_dotenv

load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "jhansi"),
    database=os.getenv("DB_NAME", "customerss"),
    port=os.getenv("DB_PORT", "3306")
)

mycursor = mydb.cursor()

# -------------------------------------------------------
# Step 1: Populate 'suppliers' table
# -------------------------------------------------------
suppliers_data = [
    ('Global Electronics Corp', 'contact@globalelec.com', 'USA'),
    ('Shenzhen Tech Solutions', 'sales@shenzhentech.cn', 'China'),
    ('EuroFurniture Co', 'supply@eurofurniture.de', 'Germany'),
    ('Apparel Manufacturers Ltd', 'hello@apparel-ltd.in', 'India'),
    ('Book Distributors Inc', 'orders@bookdistributors.com', 'UK')
]

mycursor.execute("SELECT COUNT(*) FROM suppliers")
if mycursor.fetchone()[0] == 0:
    mycursor.executemany(
        "INSERT INTO suppliers (supplier_name, contact_email, country) VALUES (%s, %s, %s)",
        suppliers_data
    )
    mydb.commit()
    print(f"{mycursor.rowcount} suppliers inserted.")

# -------------------------------------------------------
# Step 2: Populate 'inventory' table
# -------------------------------------------------------
mycursor.execute("SELECT supplier_id FROM suppliers")
supplier_ids = [row[0] for row in mycursor.fetchall()]

mycursor.execute("SELECT product_id FROM products")
product_ids = [row[0] for row in mycursor.fetchall()]

if supplier_ids and product_ids:
    mycursor.execute("SELECT COUNT(*) FROM inventory")
    if mycursor.fetchone()[0] == 0:
        inventory_data = []
        for p_id in product_ids:
            s_id = random.choice(supplier_ids)
            stock = random.randint(15, 200)
            reorder = random.randint(10, 50)
            inventory_data.append((p_id, s_id, stock, reorder))
            
        mycursor.executemany(
            "INSERT INTO inventory (product_id, supplier_id, stock_quantity, reorder_level) VALUES (%s, %s, %s, %s)",
            inventory_data
        )
        mydb.commit()
        print(f"{mycursor.rowcount} inventory records inserted.")
else:
    print("Cannot insert inventory: Need existing products and suppliers.")

# -------------------------------------------------------
# Step 3: Populate 'shipments' and 'payments' tables
# -------------------------------------------------------
# We need to map payments and shipments to existing orders
mycursor.execute("""
    SELECT o.order_id, (o.quantity * p.price) AS total_price 
    FROM orders o 
    JOIN products p ON o.product_id = p.product_id
""")
orders_data = mycursor.fetchall()

if orders_data:
    # Check if shipments are empty
    mycursor.execute("SELECT COUNT(*) FROM shipments")
    if mycursor.fetchone()[0] == 0:
        shipments_data = []
        carriers = ['FedEx', 'UPS', 'DHL', 'USPS']
        statuses = ['Shipped', 'Delivered', 'Pending', 'Delivered', 'Delivered'] # higher chance of delivered
        
        for order in orders_data:
            order_id = order[0]
            carrier = random.choice(carriers)
            status = random.choice(statuses)
            shipments_data.append((order_id, status, carrier))
            
        mycursor.executemany(
            "INSERT INTO shipments (order_id, delivery_status, carrier) VALUES (%s, %s, %s)",
            shipments_data
        )
        mydb.commit()
        print(f"{mycursor.rowcount} shipment records inserted.")
        
    # Check if payments are empty
    mycursor.execute("SELECT COUNT(*) FROM payments")
    if mycursor.fetchone()[0] == 0:
        payments_data = []
        methods = ['Credit Card', 'PayPal', 'Apple Pay', 'Bank Transfer']
        pay_statuses = ['Completed', 'Completed', 'Completed', 'Refunded', 'Failed']
        
        for order in orders_data:
            order_id = order[0]
            total_price = order[1]
            method = random.choice(methods)
            status = random.choice(pay_statuses)
            payments_data.append((order_id, method, total_price, status))
            
        mycursor.executemany(
            "INSERT INTO payments (order_id, payment_method, amount_paid, payment_status) VALUES (%s, %s, %s, %s)",
            payments_data
        )
        mydb.commit()
        print(f"{mycursor.rowcount} payment records inserted.")
else:
    print("Cannot insert shipments/payments: Need existing orders.")

# -------------------------------------------------------
# Verification
# -------------------------------------------------------
for table in ['suppliers', 'inventory', 'shipments', 'payments']:
    mycursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = mycursor.fetchone()[0]
    print(f"  '{table}' table has {count} rows")

mydb.close()
print("\nLogistics data populated successfully!")

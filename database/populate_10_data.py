import mysql.connector
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

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
# Step 1: Insert dummy promotions
# -------------------------------------------------------
promotions_data = [
    ('SUMMER20', 20.00, '2026-06-01', '2026-08-31'),
    ('BLACKFRIDAY', 30.00, '2026-11-20', '2026-11-30'),
    ('NEWYEAR10', 10.00, '2025-12-25', '2026-01-05'),
    ('FREESHIP', 5.00, '2026-01-01', '2026-12-31'),
    ('WELCOME15', 15.00, '2026-01-01', '2026-12-31')
]

mycursor.execute("SELECT COUNT(*) FROM promotions")
if mycursor.fetchone()[0] == 0:
    print("Inserting mock promotion campaigns...")
    mycursor.executemany(
        "INSERT INTO promotions (code, discount_percentage, start_date, end_date) VALUES (%s, %s, %s, %s)",
        promotions_data
    )
    mydb.commit()
    print(f"{mycursor.rowcount} promotion records inserted successfully.")
else:
    print("Promotions data already exists.")

# -------------------------------------------------------
# Step 2: Link promotions to existing orders
# -------------------------------------------------------
mycursor.execute("SELECT promotion_id FROM promotions")
promotion_ids = [row[0] for row in mycursor.fetchall()]

mycursor.execute("SELECT order_id FROM orders")
order_ids = [row[0] for row in mycursor.fetchall()]

if order_ids and promotion_ids:
    print("Linking subset of orders to promotions...")
    # Update approximately 40% of orders with a random promotion_id
    num_to_link = int(len(order_ids) * 0.4)
    orders_to_link = random.sample(order_ids, num_to_link)
    
    update_data = []
    for o_id in orders_to_link:
        promo_id = random.choice(promotion_ids)
        update_data.append((promo_id, o_id))
        
    mycursor.executemany(
        "UPDATE orders SET promotion_id = %s WHERE order_id = %s",
        update_data
    )
    mydb.commit()
    print(f"{len(update_data)} orders successfully linked to promotion codes.")
else:
    print("Could not link promotions: Make sure orders and promotions exist.")

# -------------------------------------------------------
# Step 3: Insert dummy returns
# -------------------------------------------------------
mycursor.execute("SELECT COUNT(*) FROM returns")
if mycursor.fetchone()[0] == 0:
    if order_ids:
        print("Generating mock return records (RMAs)...")
        # Approximately 10% of orders get returned
        num_returns = max(1, int(len(order_ids) * 0.1))
        orders_for_returns = random.sample(order_ids, num_returns)
        
        return_reasons = [
            'Defective product / stopped working',
            'Wrong size / fit issues',
            'Changed my mind / no longer needed',
            'Arrived too late for event',
            'Damaged in transit / broken packaging',
            'Item did not match description'
        ]
        return_statuses = ['Processing', 'Approved', 'Rejected']
        
        returns_to_insert = []
        for o_id in orders_for_returns:
            reason = random.choice(return_reasons)
            status = random.choice(return_statuses)
            # Create a return date roughly 1 to 14 days after today or default current time
            # For mockup data, we can use the default or a formatted string
            # Let's insert return_date as a timestamp from recent days
            ret_date = datetime.now() - timedelta(days=random.randint(1, 10))
            returns_to_insert.append((o_id, ret_date.strftime('%Y-%m-%d %H:%M:%S'), reason, status))
            
        mycursor.executemany(
            "INSERT INTO returns (order_id, return_date, reason, status) VALUES (%s, %s, %s, %s)",
            returns_to_insert
        )
        mydb.commit()
        print(f"{mycursor.rowcount} return records inserted successfully.")
    else:
        print("Cannot insert returns: No existing orders found.")
else:
    print("Returns data already exists.")

# -------------------------------------------------------
# Verification
# -------------------------------------------------------
print("\nVerification counts:")
for table in ['promotions', 'returns']:
    mycursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = mycursor.fetchone()[0]
    print(f"  '{table}' table has {count} rows")

mycursor.execute("SELECT COUNT(*) FROM orders WHERE promotion_id IS NOT NULL")
promo_orders_count = mycursor.fetchone()[0]
print(f"  'orders' with applied promotion codes: {promo_orders_count}")

mycursor.close()
mydb.close()
print("\nData population for 10/10 schema completed successfully!")

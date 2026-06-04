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
# Step 1: Populate 'stores' table
# -------------------------------------------------------
stores_data = [
    ('Tech Hub NYC', 'New York'),
    ('Silicon Valley Store', 'San Francisco'),
    ('Downtown Chicago', 'Chicago')
]

mycursor.execute("SELECT COUNT(*) FROM stores")
if mycursor.fetchone()[0] == 0:
    mycursor.executemany(
        "INSERT INTO stores (store_name, city) VALUES (%s, %s)",
        stores_data
    )
    mydb.commit()
    print(f"{mycursor.rowcount} stores inserted.")

# -------------------------------------------------------
# Step 2: Populate 'employees' table
# -------------------------------------------------------
employees_data = [
    ('Alice Johnson', 'Manager', 85000.00, 1),
    ('Bob Smith', 'Sales Associate', 45000.00, 1),
    ('Charlie Brown', 'Tech Support', 55000.00, 1),
    ('Diana Prince', 'Manager', 90000.00, 2),
    ('Evan Davis', 'Sales Associate', 48000.00, 2),
    ('Fiona Gallagher', 'Cashier', 35000.00, 2),
    ('George Miller', 'Manager', 82000.00, 3),
    ('Hannah Lee', 'Sales Associate', 46000.00, 3),
    ('Ian Wright', 'Inventory Specialist', 50000.00, 3),
    ('Julia Chang', 'Sales Associate', 47000.00, 1)
]

mycursor.execute("SELECT COUNT(*) FROM employees")
if mycursor.fetchone()[0] == 0:
    mycursor.executemany(
        "INSERT INTO employees (name, position, salary, store_id) VALUES (%s, %s, %s, %s)",
        employees_data
    )
    mydb.commit()
    print(f"{mycursor.rowcount} employees inserted.")

# -------------------------------------------------------
# Step 3: Populate 'reviews' table
# -------------------------------------------------------
# Get existing product_ids and customer_ids
mycursor.execute("SELECT product_id FROM products")
product_ids = [row[0] for row in mycursor.fetchall()]

mycursor.execute("SELECT customer_id FROM customers")
customer_ids = [row[0] for row in mycursor.fetchall()]

if product_ids and customer_ids:
    mycursor.execute("SELECT COUNT(*) FROM reviews")
    if mycursor.fetchone()[0] == 0:
        reviews_data = []
        comments = [
            "Great product, highly recommend!",
            "Decent, but could be better.",
            "Absolutely love it.",
            "Not worth the price.",
            "Exceeded my expectations.",
            "Average quality.",
            "Terrible experience, broke after a week.",
            "Will definitely buy again.",
            "Good value for money.",
            "Fast shipping, item as described."
        ]
        
        # Generate 30 random reviews
        for _ in range(30):
            p_id = random.choice(product_ids)
            c_id = random.choice(customer_ids)
            rating = random.randint(1, 5)
            comment = random.choice(comments)
            reviews_data.append((p_id, c_id, rating, comment))
            
        mycursor.executemany(
            "INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES (%s, %s, %s, %s)",
            reviews_data
        )
        mydb.commit()
        print(f"{mycursor.rowcount} reviews inserted.")
else:
    print("Cannot insert reviews: Need existing products and customers.")

# -------------------------------------------------------
# Verification
# -------------------------------------------------------
for table in ['stores', 'employees', 'reviews']:
    mycursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = mycursor.fetchone()[0]
    print(f"  '{table}' table has {count} rows")

mydb.close()
print("\nExtended data populated successfully!")

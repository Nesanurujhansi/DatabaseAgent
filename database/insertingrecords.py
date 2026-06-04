import mysql.connector

mydb = mysql.connector.connect(
host="localhost",
user="root",
password="jhansi",
database="customerss"
)

mycursor = mydb.cursor()

sql = """
INSERT INTO customerss
(customer_name, email, phone, city, product_name, category, quantity, price)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

customers = [
("Arjun Kumar", "[arjun@gmail.com](mailto:arjun@gmail.com)", "9876543210", "Chennai", "Wireless Mouse", "Electronics", 2, 799),
("Priya Sharma", "[priya@gmail.com](mailto:priya@gmail.com)", "9876543211", "Bangalore", "T-Shirt", "Fashion", 3, 499),
("Rahul Verma", "[rahul@gmail.com](mailto:rahul@gmail.com)", "9876543212", "Hyderabad", "Smart Watch", "Electronics", 1, 2999),
("Sneha Reddy", "[sneha@gmail.com](mailto:sneha@gmail.com)", "9876543213", "Chennai", "Running Shoes", "Footwear", 1, 2499),
("Karthik Raj", "[karthik@gmail.com](mailto:karthik@gmail.com)", "9876543214", "Coimbatore", "Bluetooth Speaker", "Electronics", 1, 1599),
("Anjali Gupta", "[anjali@gmail.com](mailto:anjali@gmail.com)", "9876543215", "Mumbai", "Handbag", "Fashion", 2, 899),
("Vikram Singh", "[vikram@gmail.com](mailto:vikram@gmail.com)", "9876543216", "Delhi", "Laptop Bag", "Accessories", 1, 1299),
("Deepika Nair", "[deepika@gmail.com](mailto:deepika@gmail.com)", "9876543217", "Kochi", "Mixer Grinder", "Home Appliances", 1, 3499),
("Naveen Kumar", "[naveen@gmail.com](mailto:naveen@gmail.com)", "9876543218", "Chennai", "Mobile Phone", "Electronics", 1, 18999),
("Pooja Patel", "[pooja@gmail.com](mailto:pooja@gmail.com)", "9876543219", "Ahmedabad", "Water Bottle", "Home & Kitchen", 4, 299),
("Ramesh Babu", "[ramesh@gmail.com](mailto:ramesh@gmail.com)", "9876543220", "Vijayawada", "Keyboard", "Electronics", 1, 899),
("Keerthi Rao", "[keerthi@gmail.com](mailto:keerthi@gmail.com)", "9876543221", "Bangalore", "Headphones", "Electronics", 1, 1999),
("Suresh Yadav", "[suresh@gmail.com](mailto:suresh@gmail.com)", "9876543222", "Hyderabad", "Power Bank", "Electronics", 2, 999),
("Lavanya Sri", "[lavanya@gmail.com](mailto:lavanya@gmail.com)", "9876543223", "Chennai", "Saree", "Fashion", 1, 2499),
("Manoj Kumar", "[manoj@gmail.com](mailto:manoj@gmail.com)", "9876543224", "Pune", "Gaming Mouse", "Electronics", 1, 1499),
("Harini Devi", "[harini@gmail.com](mailto:harini@gmail.com)", "9876543225", "Madurai", "Face Cream", "Beauty", 2, 599),
("Ajay Sharma", "[ajay@gmail.com](mailto:ajay@gmail.com)", "9876543226", "Delhi", "LED Monitor", "Electronics", 1, 8999),
("Bhavana R", "[bhavana@gmail.com](mailto:bhavana@gmail.com)", "9876543227", "Mysore", "Coffee Maker", "Home Appliances", 1, 2799),
("Kishore Reddy", "[kishore@gmail.com](mailto:kishore@gmail.com)", "9876543228", "Warangal", "Study Table", "Furniture", 1, 4999),
("Meena Lakshmi", "[meena@gmail.com](mailto:meena@gmail.com)", "9876543229", "Trichy", "Curtains", "Home Decor", 3, 799)
]

mycursor.executemany(sql, customers)

mydb.commit()

print(mycursor.rowcount, "records inserted successfully")

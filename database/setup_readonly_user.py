import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# We connect using the existing root/admin credentials
admin_user = os.getenv("DB_USER", "root")
admin_password = os.getenv("DB_PASSWORD", "jhansi")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME", "customerss")

print(f"Connecting to MySQL as admin '{admin_user}' to configure read-only privileges...")

try:
    mydb = mysql.connector.connect(
        host=db_host,
        user=admin_user,
        password=admin_password,
        port=db_port
    )
    mycursor = mydb.cursor()
    
    # 1. Create read-only user for localhost
    print("Creating 'readonly_user'@'localhost'...")
    mycursor.execute("CREATE USER IF NOT EXISTS 'readonly_user'@'localhost' IDENTIFIED BY 'readonly_pass'")
    
    # 2. Grant SELECT privileges only on the target database
    print(f"Granting SELECT on {db_name}.* to 'readonly_user'@'localhost'...")
    mycursor.execute(f"GRANT SELECT ON {db_name}.* TO 'readonly_user'@'localhost'")
    
    # 3. Create read-only user for any host wildcard
    print("Creating 'readonly_user'@'%'...")
    mycursor.execute("CREATE USER IF NOT EXISTS 'readonly_user'@'%' IDENTIFIED BY 'readonly_pass'")
    
    print(f"Granting SELECT on {db_name}.* to 'readonly_user'@'%'...")
    mycursor.execute(f"GRANT SELECT ON {db_name}.* TO 'readonly_user'@'%'")
    
    # 4. Flush privileges
    mycursor.execute("FLUSH PRIVILEGES")
    print("Privileges flushed successfully.")
    
    mycursor.close()
    mydb.close()
    print("\nRead-only MySQL user setup complete!")
except Exception as e:
    print(f"Error setting up read-only user: {e}")

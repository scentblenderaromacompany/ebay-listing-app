import sqlite3

# Database file path
db_path = "../database/ebay_listing.db"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Clear the sku_tracker table
cursor.execute('DELETE FROM sku_tracker')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database SKU counter reset successfully.")

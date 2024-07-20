import sqlite3
import os

# Database file path
db_path = "/home/robertmcasper/ebay-listing-app/database/ebay_listing.db"
db_dir = os.path.dirname(db_path)

# Create the directory if it doesn't exist
os.makedirs(db_dir, exist_ok=True)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table for SKU tracking if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS sku_tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_number INTEGER NOT NULL,
    date_processed TEXT NOT NULL,
    subfolder_count INTEGER NOT NULL,
    image_count INTEGER NOT NULL
)
''')

# Clear the sku_tracker table
cursor.execute('DELETE FROM sku_tracker')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database SKU counter reset successfully.")

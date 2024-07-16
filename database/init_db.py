import sqlite3

# Database file path
db_path = "../database/ebay_listing.db"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table for SKU tracking
cursor.execute('''
CREATE TABLE IF NOT EXISTS sku_tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku_number INTEGER NOT NULL,
    date_processed TEXT NOT NULL,
    subfolder_count INTEGER NOT NULL,
    image_count INTEGER NOT NULL
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database initialized successfully.")

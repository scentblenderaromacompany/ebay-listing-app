import sqlite3

# Database file path
db_path = "/home/robertmcasper/Repos/ebay-listing-app/database/ebay_listing.db"

# New SKU number to start from
new_sku_number = 0

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Clear the sku_tracker table
cursor.execute('DELETE FROM sku_tracker')

# Insert a new initial SKU number
cursor.execute('INSERT INTO sku_tracker (sku_number, date_processed, subfolder_count, image_count) VALUES (?, ?, ?, ?)', 
               (new_sku_number, '1970-01-01', 0, 0))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database SKU counter updated successfully.")

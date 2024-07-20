import os
import shutil
from datetime import datetime
import sqlite3
import logging
import colorlog

# Paths
input_dir = "/home/robertmcasper/ebay-listing-app/input/raw/images"
output_dir = "/home/robertmcasper/ebay-listing-app/output/processed/images"
db_path = "../database/ebay_listing.db"
log_file_path = "../logs/application.log"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)
os.makedirs("../database", exist_ok=True)
os.makedirs("../logs", exist_ok=True)

# Configure logging
log_colors = {
    'DEBUG': 'bold_blue',
    'INFO': 'bold_green',
    'WARNING': 'bold_yellow',
    'ERROR': 'bold_red',
    'CRITICAL': 'bold_red,bg_white',
}

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors=log_colors
)

file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
))

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])

logger = logging.getLogger()

def get_last_sku_number():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT sku_number FROM sku_tracker ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_sku_tracker(sku_number, date_processed, subfolder_count, image_count):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sku_tracker (sku_number, date_processed, subfolder_count, image_count)
        VALUES (?, ?, ?, ?)
    ''', (sku_number, date_processed, subfolder_count, image_count))
    conn.commit()
    conn.close()

def process_folders():
    current_sku = get_last_sku_number()
    date_str = datetime.now().strftime("%m_%d_%Y_%I:%M%p")

    for main_folder in os.listdir(input_dir):
        main_folder_path = os.path.join(input_dir, main_folder)
        if os.path.isdir(main_folder_path):
            logger.info(f"Processing main folder: {main_folder}")
            subfolders = [f for f in os.listdir(main_folder_path) if os.path.isdir(os.path.join(main_folder_path, f))]
            sku_range = f"{current_sku+1:05d}-{current_sku+len(subfolders):05d}"
            new_main_folder_name = f"{date_str}_SKU#{sku_range}"
            new_main_folder_path = os.path.join(output_dir, new_main_folder_name)

            os.makedirs(new_main_folder_path, exist_ok=True)
            total_image_count = 0

            for i, subfolder in enumerate(subfolders, start=1):
                subfolder_path = os.path.join(main_folder_path, subfolder)
                image_files = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
                new_subfolder_name = f"SKU_{current_sku+i:04d}/{len(image_files)}"
                new_subfolder_path = os.path.join(new_main_folder_path, new_subfolder_name)

                os.makedirs(new_subfolder_path, exist_ok=True)
                logger.info(f"Processing subfolder: {subfolder}, New name: {new_subfolder_name}")

                for j, image_file in enumerate(image_files, start=1):
                    new_image_name = f"SKU_{current_sku+i:04d}-IMG_{j}{os.path.splitext(image_file)[1]}"
                    shutil.copy(os.path.join(subfolder_path, image_file), os.path.join(new_subfolder_path, new_image_name))

                total_image_count += len(image_files)

            current_sku += len(subfolders)
            update_sku_tracker(current_sku, date_str, len(subfolders), total_image_count)
            logger.info(f"Processed {len(subfolders)} subfolders with a total of {total_image_count} images")

if __name__ == "__main__":
    try:
        process_folders()
        logger.info("Processing completed successfully.")
    except Exception as e:
        logger.error("An error occurred during processing", exc_info=True)

import os
import logging
import requests
import base64
import yaml
import json
import colorlog
from PIL import Image, UnidentifiedImageError
import io

# Configure logging
log_colors_config = {
    'DEBUG': 'bold_blue',
    'INFO': 'bold_green',
    'WARNING': 'bold_yellow',
    'ERROR': 'bold_red',
    'CRITICAL': 'bold_red,bg_white',
}

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors=log_colors_config
))

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Load eBay credentials
with open('/home/robertmcasper/ebay-listing-app/config/ebay.yaml', 'r') as file:
    ebay_credentials = yaml.safe_load(file)

EBAY_API_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search_by_image"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ebay_credentials['api.ebay.com']['token']}"
}

def perform_ebay_image_search(image_base64):
    payload = {
        "image": image_base64
    }
    response = requests.post(EBAY_API_URL, json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_closest_match(search_results):
    items = search_results.get('itemSummaries', [])
    if not items:
        return None
    return max(items, key=lambda item: item.get('imageSearchMatchConfidence', 0))

def encode_image_to_base64(file_path):
    try:
        with Image.open(file_path) as img:
            rgb_image = img.convert('RGB')
            buffered = io.BytesIO()
            rgb_image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except (FileNotFoundError, UnidentifiedImageError) as e:
        logger.error(f"Failed to encode {file_path}: {e}")
        return None

def process_base64_files(base64_dir, search_results_dir):
    for file_name in os.listdir(base64_dir):
        if file_name.endswith(".txt"):
            file_path = os.path.join(base64_dir, file_name)
            with open(file_path, 'r') as file:
                image_base64 = file.read().strip()

            try:
                search_results = perform_ebay_image_search(image_base64)
                closest_match = get_closest_match(search_results)
                
                result_file_path = os.path.join(search_results_dir, f"{os.path.splitext(file_name)[0]}_result.json")
                with open(result_file_path, 'w') as result_file:
                    json.dump(closest_match, result_file, indent=4)
                
                logger.info(f"Processed and saved search result for {file_name}")
            except requests.RequestException as e:
                logger.error(f"Failed to perform image search for {file_name}: {e}")

def process_subfolders(output_dir):
    for root, dirs, _ in os.walk(output_dir):
        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            base64_dir = os.path.join(subdir_path, "base64")
            search_results_dir = os.path.join(subdir_path, "search_results")
            if os.path.exists(base64_dir):  # Ensure base64 directory exists before processing
                os.makedirs(search_results_dir, exist_ok=True)
                process_base64_files(base64_dir, search_results_dir)

if __name__ == "__main__":
    output_dir = '/home/robertmcasper/ebay-listing-app/output/processed/images'

    if not os.path.exists(output_dir):
        logger.error(f"Output directory does not exist: {output_dir}")
        exit(1)

    process_subfolders(output_dir)
    logger.info("Processing complete.")

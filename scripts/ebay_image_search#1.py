import os
import json
import yaml
import time
import requests
import logging
import coloredlogs
from termcolor import colored

# Set up colored logging
coloredlogs.install(level='INFO', fmt='%(asctime)s - %(levelname)s - %(message)s')

def read_base64_strings(directory):
    base64_strings = []
    base64_dir = os.path.join(directory, "base64")
    if os.path.exists(base64_dir):
        for file in os.listdir(base64_dir):
            if file.endswith(".txt"):
                file_path = os.path.join(base64_dir, file)
                with open(file_path, "r") as f:
                    base64_string = f.read()
                    base64_strings.append((file, base64_string))
    return base64_strings

def read_token_from_yaml(yaml_filename='/home/robertmcasper/ebay-listing-app/config/ebay.yaml', environment='api.ebay.com'):
    with open(yaml_filename, 'r') as file:
        config = yaml.safe_load(file)
    return config[environment]['token']

def ebay_image_search(base64_string, token, url, retries=3):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"image": base64_string}
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err} (attempt {attempt + 1}/{retries}) - Status Code: {response.status_code} - Response Content: {response.content}")
            if response.status_code == 500:
                logging.error(f"500 Server Error for URL: {url}. Skipping this image.")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        time.sleep(2 ** attempt)
    return None

def save_listing_results(directory, results):
    listing_dir = os.path.join(directory, "listing")
    os.makedirs(listing_dir, exist_ok=True)
    output_file = os.path.join(listing_dir, "listing_results.txt")
    with open(output_file, "w") as f:
        for result in results:
            f.write(f"File: {result['file']}\n")
            f.write(f"Title: {result['title']}\n")
            f.write(f"Price: {result['price']}\n")
            f.write(f"Description: {result.get('description', 'N/A')}\n")
            f.write("\n")

def process_subfolders(directory, token, environment='production'):
    base_url = "https://api.ebay.com" if environment == 'production' else "https://api.sandbox.ebay.com"
    url = f"{base_url}/buy/browse/v1/item_summary/search_by_image"
    for root, dirs, _ in os.walk(directory):
        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            base64_strings = read_base64_strings(subdir_path)
            results = []
            for file, base64_string in base64_strings:
                logging.info(colored(f"Processing file: {file}", 'blue'))
                response_data = ebay_image_search(base64_string, token, url)
                if response_data and 'itemSummaries' in response_data:
                    closest_match = response_data['itemSummaries'][0]
                    result = {
                        "file": file,
                        "title": closest_match['title'],
                        "price": closest_match['price']['value'],
                        "description": closest_match.get('shortDescription', 'N/A')
                    }
                    results.append(result)
                time.sleep(1)  # Sleep to avoid rapid consecutive requests
            if results:
                save_listing_results(subdir_path, results)

def main():
    mother_directory = "/home/robertmcasper/ebay-listing-app/output/processed/images"
    
    # Attempt to use production environment first
    token = read_token_from_yaml('/home/robertmcasper/ebay-listing-app/config/ebay.yaml', 'api.ebay.com')
    
    if token:
        try:
            process_subfolders(mother_directory, token, environment='production')
            logging.info("Image search completed and results saved using production environment.")
        except Exception as e:
            logging.error(f"Failed using production environment: {e}")
            # Fallback to sandbox environment if production fails
            logging.info("Attempting to use sandbox environment...")
            token = read_token_from_yaml('/home/robertmcasper/ebay-listing-app/config/ebay.yaml', 'api.sandbox.ebay.com')
            if token:
                process_subfolders(mother_directory, token, environment='sandbox')
                logging.info("Image search completed and results saved using sandbox environment.")
            else:
                logging.error("Failed to retrieve sandbox token.")
    else:
        logging.error("Failed to retrieve production token.")

if __name__ == "__main__":
    main()

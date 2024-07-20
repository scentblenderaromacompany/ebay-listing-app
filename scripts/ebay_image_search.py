import os
import json
import yaml
import requests
from tqdm import tqdm

def read_config(environment='production'):
    with open('/home/robertmcasper/ebay-listing-app/config/ebay.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config[f"api.{environment}.ebay.com"]

def ebay_image_search(base64_string, token, url):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
    }
    payload = {
        'image': base64_string
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.json()}")
        response.raise_for_status()

def process_subfolders(mother_directory, token, base_url):
    for subdir, dirs, files in os.walk(mother_directory):
        if 'base64' in subdir:
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(subdir, file)
                    print(f"Processing file: {file}")

                    with open(file_path, 'r') as f:
                        base64_string = f.read().strip()

                    if not base64_string:
                        print(f"Error: File {file} is empty or invalid")
                        continue

                    print(f"Base64 string (first 50 chars): {base64_string[:50]}...")  # Debugging statement

                    try:
                        response_data = ebay_image_search(base64_string, token, base_url)
                        
                        results_dir = os.path.join(os.path.dirname(subdir), 'results')
                        os.makedirs(results_dir, exist_ok=True)
                        
                        result_file_path = os.path.join(results_dir, f"{file}_results.json")
                        with open(result_file_path, 'w') as result_file:
                            json.dump(response_data, result_file, indent=2)
                        
                        print(f"Results saved to {result_file_path}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error: {e}")
                        continue

def main():
    environment = 'production'
    try:
        config = read_config(environment)
        token = config['token']
        base_url = config['base_url']
        process_subfolders('/home/robertmcasper/ebay-listing-app/output/processed/images', token, base_url)
    except KeyError as e:
        print(f"KeyError: {e}")
        print("Failed to retrieve production token or base_url.")
        environment = 'sandbox'
        config = read_config(environment)
        token = config['token']
        base_url = config['base_url']
        process_subfolders('/home/robertmcasper/ebay-listing-app/output/processed/images', token, base_url)

if __name__ == "__main__":
    main()

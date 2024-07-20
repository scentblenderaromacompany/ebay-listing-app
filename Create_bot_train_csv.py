import pandas as pd
import yaml
import os
import requests
import base64
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
import logging
from termcolor import colored

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# eBay application credentials
PROD_CLIENT_ID = 'RobertCa-EEEListi-PRD-95ebc3657-bf1bb29a'
PROD_CLIENT_SECRET = 'PRD-5ebc3657eb7b-3e82-4eaf-9ffb-5551'
SANDBOX_CLIENT_ID = 'RobertCa-EEEListi-SBX-473448ebb-3cf6b0b0'
SANDBOX_CLIENT_SECRET = 'SBX-73448ebbef34-3dd8-40bd-816d-3ef3'
DEV_ID = '84532149-06a3-4d25-8465-5912d409c098'

# eBay OAuth2 endpoints
SANDBOX_TOKEN_URL = 'https://api.sandbox.ebay.com/identity/v1/oauth2/token'
PROD_TOKEN_URL = 'https://api.ebay.com/identity/v1/oauth2/token'

# eBay OAuth2 scopes
SCOPES = 'https://api.ebay.com/oauth/api_scope'

def get_oauth_token(client_id, client_secret, token_url):
    credentials = f'{client_id}:{client_secret}'
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    body = {
        'grant_type': 'client_credentials',
        'scope': SCOPES
    }

    response = requests.post(token_url, headers=headers, data=body)
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Failed to get token: {response.status_code}")
        print(response.json())
        return None

def update_yaml_file(sandbox_token, prod_token, yaml_filename='ebay.yaml'):
    if not os.path.exists(yaml_filename):
        print(f"YAML configuration file {yaml_filename} not found!")
        return

    with open(yaml_filename, 'r') as file:
        config = yaml.safe_load(file)

    config['api.sandbox.ebay.com']['token'] = sandbox_token
    config['api.ebay.com']['token'] = prod_token

    config['api.sandbox.ebay.com']['appid'] = SANDBOX_CLIENT_ID
    config['api.sandbox.ebay.com']['certid'] = SANDBOX_CLIENT_SECRET
    config['api.sandbox.ebay.com']['devid'] = DEV_ID

    config['api.ebay.com']['appid'] = PROD_CLIENT_ID
    config['api.ebay.com']['certid'] = PROD_CLIENT_SECRET
    config['api.ebay.com']['devid'] = DEV_ID

    config['svcs.ebay.com']['appid'] = PROD_CLIENT_ID
    config['open.api.ebay.com']['appid'] = PROD_CLIENT_ID

    with open(yaml_filename, 'w') as file:
        yaml.safe_dump(config, file)

def get_ebay_listings(credentials, environment='production', entries_per_page=10):
    api = Trading(config_file=None, appid=credentials['appid'], certid=credentials['certid'], 
                  devid=credentials['devid'], token=credentials['token'], siteid=credentials['siteid'])
    
    listings = []
    page_number = 1
    
    while True:
        try:
            response = api.execute('GetMyeBaySelling', {
                'ActiveList': {
                    'Include': True,
                    'Pagination': {
                        'EntriesPerPage': entries_per_page,
                        'PageNumber': page_number
                    }
                },
                'DetailLevel': 'ReturnAll'
            })
            
            # Log the entire response for debugging
            logging.info(f"API Response for {environment} environment for store {credentials['username']}: {response.dict()}")

            active_list = response.dict().get('ActiveList', {})
            if not active_list:
                logging.info(f"No ActiveList found in response for store {credentials['username']}.")
                break

            items = active_list.get('ItemArray', {}).get('Item', [])
            if not items:
                logging.info(f"No items found in ActiveList for page {page_number}.")
                break
            
            for item in items:
                listings.append({
                    'ItemID': item.get('ItemID'),
                    'Title': item.get('Title'),
                    'CategoryID': item.get('PrimaryCategory', {}).get('CategoryID'),
                    'Price': item.get('SellingStatus', {}).get('CurrentPrice', {}).get('value'),
                    'Description': item.get('Description')[:100]  # Short description
                })
            
            page_number += 1
        except ConnectionError as e:
            logging.error(f"Connection Error for {environment} environment for store {credentials['username']}: {e}")
            logging.error(f"Response: {e.response.dict()}")
            break
        except Exception as e:
            logging.error(f"Unexpected error for {environment} environment for store {credentials['username']}: {e}")
            break
    
    return pd.DataFrame(listings)

def main():
    # Fetch tokens
    sandbox_token = get_oauth_token(SANDBOX_CLIENT_ID, SANDBOX_CLIENT_SECRET, SANDBOX_TOKEN_URL)
    prod_token = get_oauth_token(PROD_CLIENT_ID, PROD_CLIENT_SECRET, PROD_TOKEN_URL)
    
    if sandbox_token and prod_token:
        update_yaml_file(sandbox_token, prod_token)
        print("Tokens updated in ebay.yaml")

        # Load updated credentials
        with open('ebay.yaml', 'r') as file:
            config = yaml.safe_load(file)

        PROD_CREDENTIALS = {
            'appid': config['api.ebay.com']['appid'],
            'certid': config['api.ebay.com']['certid'],
            'devid': config['api.ebay.com']['devid'],
            'token': config['api.ebay.com']['token'],
            'siteid': config['api.ebay.com']['siteid'],
            'username': 'Eternal_Elegance_Emporium'  # Updated production username
        }

        SANDBOX_CREDENTIALS = {
            'appid': config['api.sandbox.ebay.com']['appid'],
            'certid': config['api.sandbox.ebay.com']['certid'],
            'devid': config['api.sandbox.ebay.com']['devid'],
            'token': config['api.sandbox.ebay.com']['token'],
            'siteid': config['api.sandbox.ebay.com']['siteid'],
            'username': 'testuser_bzcasper'  # Updated sandbox username
        }

        # Try fetching from production environment
        inventory_df = get_ebay_listings(PROD_CREDENTIALS, 'production')
        
        if inventory_df.empty:
            logging.info(f"No listings found in production environment. Switching to sandbox environment.")
            inventory_df = get_ebay_listings(SANDBOX_CREDENTIALS, 'sandbox')
        
        if not inventory_df.empty:
            # Save the dataset for training purposes
            inventory_df.to_csv('ebay_inventory.csv', index=False)
            print(inventory_df)
        else:
            logging.info(f"No listings found for store {PROD_CREDENTIALS['username']}.")
    else:
        print("Failed to retrieve tokens.")

if __name__ == "__main__":
    main()

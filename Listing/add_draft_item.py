# /home/robertmcasper/ebay-listing-app/Listing/add_draft_item.py
import sys
import os
import requests

# Add the config directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from config_loader import load_ebay_config, get_ebay_token

def create_draft_item(sku, offer_details, config_path, env='production'):
    config = load_ebay_config(config_path)
    token = get_ebay_token(config, env)
    url = "https://api.ebay.com/sell/inventory/v1/offer"
    headers = {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=offer_details)
    if response.status_code == 201:
        offer_id = response.json().get('offerId')
        print(f"Successfully created draft item. Offer ID: {offer_id}")
    else:
        print(f"Failed to create draft item. Status code: {response.status_code}, Response: {response.json()}")

# Example usage
if __name__ == "__main__":
    config_path = '/home/robertmcasper/ebay-listing-app/config/ebay.yaml'
    sku = "unique_sku_123"
    offer_details = {
        "sku": sku,
        "marketplaceId": "EBAY_US",
        "format": "FIXED_PRICE",
        "listingDescription": "A beautiful piece of jewelry",
        "availableQuantity": 10,
        "pricingSummary": {
            "price": {
                "value": 99.99,
                "currency": "USD"
            }
        }
    }
    create_draft_item(sku, offer_details, config_path)

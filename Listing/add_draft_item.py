import requests
import csv
import os
import logging
import yaml

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the configuration file
CONFIG_PATH = '/home/robertmcasper/ebay-listing-app/config/ebay.yaml'

def load_config(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

config = load_config(CONFIG_PATH)
environment = 'production.ebay.com'  # Set to production environment

APP_ID = config['api'][environment]['appid']
CERT_ID = config['api'][environment]['certid']
DEV_ID = config['api'][environment]['devid']
USER_TOKEN = config['api'][environment]['token']
EBAY_API_URL = 'https://api.ebay.com/ws/api.dll'

def get_headers(api_call_name):
    headers = {
        'Content-Type': 'text/xml',
        'X-EBAY-API-COMPATIBILITY-LEVEL': str(config['api'][environment]['compatability']),
        'X-EBAY-API-DEV-NAME': DEV_ID,
        'X-EBAY-API-APP-NAME': APP_ID,
        'X-EBAY-API-CERT-NAME': CERT_ID,
        'X-EBAY-API-CALL-NAME': api_call_name,
        'X-EBAY-API-SITEID': str(config['api'][environment]['siteid']),
    }
    return headers

def create_draft_listing(title, description, price, category_id, condition_id, image_url):
    valid_condition_ids = ["1000", "1500", "1750", "2000", "2500", "3000", "4000", "5000", "6000", "7000"]

    if condition_id not in valid_condition_ids:
        logging.error(f"Invalid ConditionID: {condition_id}")
        return

    request_payload = f"""<?xml version="1.0" encoding="utf-8"?>
    <AddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
      <RequesterCredentials>
        <eBayAuthToken>{USER_TOKEN}</eBayAuthToken>
      </RequesterCredentials>
      <ErrorLanguage>en_US</ErrorLanguage>
      <WarningLevel>High</WarningLevel>
      <Item>
        <Title>{title}</Title>
        <Description>{description}</Description>
        <PrimaryCategory>
          <CategoryID>{category_id}</CategoryID>
        </PrimaryCategory>
        <StartPrice>{price}</StartPrice>
        <ConditionID>{condition_id}</ConditionID>
        <Country>US</Country>
        <Currency>USD</Currency>
        <DispatchTimeMax>3</DispatchTimeMax>
        <ListingDuration>GTC</ListingDuration>
        <ListingType>FixedPriceItem</ListingType>
        <PaymentMethods>PayPal</PaymentMethods>
        <PayPalEmailAddress>example@example.com</PayPalEmailAddress>
        <PictureDetails>
          <PictureURL>{image_url}</PictureURL>
        </PictureDetails>
        <PostalCode>95125</PostalCode>
        <Quantity>1</Quantity>
        <ReturnPolicy>
          <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
          <RefundOption>MoneyBack</RefundOption>
          <ReturnsWithinOption>Days_30</ReturnsWithinOption>
          <Description>If you are not satisfied, return the item for refund.</Description>
          <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
        </ReturnPolicy>
        <ShippingDetails>
          <ShippingType>Flat</ShippingType>
          <ShippingServiceOptions>
            <ShippingServicePriority>1</ShippingServicePriority>
            <ShippingService>USPSPriority</ShippingService>
            <ShippingServiceCost>0.00</ShippingServiceCost>
          </ShippingServiceOptions>
        </ShippingDetails>
        <Site>US</Site>
      </Item>
      <Action>Draft</Action>
    </AddItemRequest>"""

    response = requests.post(EBAY_API_URL, headers=get_headers('AddItem'), data=request_payload)
    if response.status_code == 200:
        logging.info("Item draft created successfully!")
        logging.debug(response.text)
    else:
        logging.error("Failed to create item draft")
        logging.debug(response.text)

def read_csv_and_create_draft_listings(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            create_draft_listing(
                title=row['Title'],
                description=row['Description'],
                price=row['Price'],
                category_id=row['Category ID'],
                condition_id=row['Condition ID'],
                image_url=row['Item photo URL']
            )

# Example CSV file path
csv_file_path = 'listings.csv'

# Call the function to read the CSV and create draft listings
if os.path.exists(csv_file_path):
    read_csv_and_create_draft_listings(csv_file_path)
else:
    logging.error(f"CSV file not found: {csv_file_path}")

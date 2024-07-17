# /home/robertmcasper/ebay-listing-app/Listing/add_inventory_item.py

import sys
import os
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError

# Add the config directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from config_loader import load_ebay_config, get_ebay_token

def add_inventory_item(item_details, config_path, env='api.ebay.com'):
    config = load_ebay_config(config_path)
    token = get_ebay_token(config, env)
    try:
        api = Trading(domain=env, appid=config[env]['appid'], certid=config[env]['certid'], devid=config[env]['devid'], token=token, config_file=None)
        response = api.execute('AddFixedPriceItem', item_details)
        if response.reply.Ack == 'Success':
            print(f"Successfully added item: {response.reply.ItemID}")
        else:
            print(f"Failed to add item: {response.reply.Errors}")
    except ConnectionError as e:
        print(e)
        print(e.response.dict())

# Example usage
if __name__ == "__main__":
    config_path = '/home/robertmcasper/ebay-listing-app/config/ebay.yaml'
    item_details = {
        "Item": {
            "Title": "Sample Jewelry Item",
            "Description": "A beautiful piece of jewelry",
            "PrimaryCategory": {"CategoryID": "11116"},
            "StartPrice": {"currencyID": "USD", "value": 99.99},
            "ConditionID": 1000,
            "Country": "US",
            "Currency": "USD",
            "DispatchTimeMax": 3,
            "ListingDuration": "GTC",
            "ListingType": "FixedPriceItem",
            "PaymentMethods": ["PayPal"],
            "PayPalEmailAddress": "example@example.com",
            "PictureDetails": {
                "GalleryType": "Gallery",
                "PictureURL": [
                    "http://example.com/image1.jpg",
                    "http://example.com/image2.jpg"
                ]
            },
            "PostalCode": "95125",
            "Quantity": 10,
            "ReturnPolicy": {
                "ReturnsAcceptedOption": "ReturnsAccepted",
                "RefundOption": "MoneyBack",
                "ReturnsWithinOption": "Days_30",
                "ShippingCostPaidByOption": "Buyer"
            },
            "ShippingDetails": {
                "ShippingType": "Flat",
                "ShippingServiceOptions": [
                    {
                        "ShippingServicePriority": 1,
                        "ShippingService": "USPSMedia",
                        "FreeShipping": True,
                        "ShippingServiceCost": {"currencyID": "USD", "value": 0.0}
                    }
                ]
            },
            "Site": "US",
            "SKU": "ABC123",
            "CategoryMappingAllowed": True,
            "ConditionDescription": "Brand new with tags",
            "CrossBorderTrade": ["UK", "AU"],
            "GlobalShipping": True,
            "ItemSpecifics": {
                "NameValueList": [
                    {"Name": "Brand", "Value": "Unbranded"},
                    {"Name": "Style", "Value": "Pendant"}
                ]
            },
            "PaymentInstructions": "Pay within 3 days",
            "ShippingPackageDetails": {
                "ShippingIrregular": False,
                "ShippingPackage": "PackageThickEnvelope",
                "WeightMajor": {"unit": "lbs", "value": 1},
                "WeightMinor": {"unit": "oz", "value": 0}
            },
            "Storefront": {
                "StoreCategoryID": 41528601010,
                "StoreCategory2ID": 41528601010,
                "StoreURL": "https://www.ebay.com/str/eternaleleganceemporium"
            }
        }
    }
    add_inventory_item(item_details, config_path)

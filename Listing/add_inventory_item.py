# /home/robertmcasper/ebay-listing-app/Listing/add_inventory_item.=
# Add the config directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

def load_ebay_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['api']

def get_ebay_token(config, env):
    try:
        return config[env]['token']
    except KeyError:
        raise KeyError(f"The environment '{env}' is not found in the configuration or the token is missing.")

def create_ebay_connection(config, env, token):
    try:
        return Trading(
            domain=env,
            appid=config[env]['appid'],
            certid=config[env]['certid'],
            devid=config[env]['devid'],
            token=token,
            config_file=None
        )
    except KeyError as e:
        raise KeyError(f"Missing key in configuration: {e}")

def add_inventory_item(item_details, config_path, env='production.ebay.com'):
    config = load_ebay_config(config_path)
    if env not in config:
        print(f"Error: The environment '{env}' is not found in the configuration.")
        return
    
    try:
        token = get_ebay_token(config, env)
        api = create_ebay_connection(config, env, token)
        response = api.execute('AddFixedPriceItem', item_details)
        if response.reply.Ack == 'Success':
            print(f"Successfully added item: {response.reply.ItemID}")
        else:
            print(f"Failed to add item: {response.reply.Errors}")
    except ConnectionError as e:
        print(f"Connection error: {e}")
        if e.response:
            print(e.response.dict())
    except KeyError as e:
        print(f"Configuration error: {e}")

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

import requests
import yaml
import logging

logging.basicConfig(level=logging.INFO)

def generate_oauth_token(client_id, client_secret, environment="sandbox"):
    url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token" if environment == "sandbox" else "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    try:
        response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
        response.raise_for_status()
        return response.json()['access_token']
    except requests.HTTPError as e:
        logging.error(f"Failed to get token for {environment} environment: {e}")
        raise

def validate_token(token, environment="sandbox"):
    url = "https://api.sandbox.ebay.com/ws/api.dll" if environment == "sandbox" else "https://api.ebay.com/ws/api.dll"
    headers = {
        "X-EBAY-API-CALL-NAME": "GeteBayOfficialTime",
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-APP-ID": token,
        "X-EBAY-API-VERSION": "967",
        "X-EBAY-API-REQUEST-ENCODING": "XML",
        "Content-Type": "text/xml"
    }
    body = """<?xml version="1.0" encoding="utf-8"?>
                <GeteBayOfficialTimeRequest xmlns="urn:ebay:apis:eBLBaseComponents">
                </GeteBayOfficialTimeRequest>"""
    response = requests.post(url, headers=headers, data=body)
    if response.status_code == 200:
        logging.info(f"Token for {environment} environment is valid.")
        return True
    else:
        logging.error(f"Invalid token for {environment} environment.")
        return False

def update_yaml_file(sandbox_token, production_token, yaml_path):
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)

    config['api.sandbox.ebay.com']['token'] = sandbox_token
    config['api.ebay.com']['token'] = production_token

    with open(yaml_path, 'w') as file:
        yaml.safe_dump(config, file)

if __name__ == "__main__":
    sandbox_client_id = "RobertCa-EEEListi-SBX-473448ebb-3cf6b0b0"
    sandbox_client_secret = "SBX-73448ebbef34-3dd8-40bd-816d-3ef3"
    production_client_id = "RobertCa-EEEListi-PRD-95ebc3657-bf1bb29a"
    production_client_secret = "PRD-5ebc3657eb7b-3e82-4eaf-9ffb-5551"

    sandbox_token = generate_oauth_token(sandbox_client_id, sandbox_client_secret, environment="sandbox")
    if not validate_token(sandbox_token, environment="sandbox"):
        logging.error("Failed to get a valid sandbox token.")
        exit(1)

    production_token = None
    try:
        production_token = generate_oauth_token(production_client_id, production_client_secret, environment="production")
    except requests.HTTPError:
        logging.info("Failed to get production token, will use sandbox token if valid.")

    if production_token and not validate_token(production_token, environment="production"):
        logging.info("Using sandbox token for production environment.")
        production_token = sandbox_token

    yaml_path = '/home/robertmcasper/ebay-listing-app/config/ebay.yaml'
    update_yaml_file(sandbox_token, production_token, yaml_path)

    logging.info("Tokens updated in ebay.yaml")

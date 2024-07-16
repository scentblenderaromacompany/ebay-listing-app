import requests
import yaml

def generate_oauth_token(client_id, client_secret, environment="sandbox"):
    if environment == "production":
        url = "https://api.ebay.com/identity/v1/oauth2/token"
    else:
        url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
    response.raise_for_status()
    return response.json()['access_token']

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
    production_token = generate_oauth_token(production_client_id, production_client_secret, environment="production")
    
    yaml_path = '/home/robertmcasper/ebay-listing-app/config/ebay.yaml'
    update_yaml_file(sandbox_token, production_token, yaml_path)
    
    print("Tokens updated in ebay.yaml")

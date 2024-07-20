import yaml

def load_ebay_config(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def get_ebay_token(config, env='api.ebay.com'):
    return config[env]['token']

class GrocyConfig:
    def __init__(self, config: dict):
        self.base_url = config["base_url"]
        self.api_key = config["api_key"]

    def __repr__(self):
        return f"Grocy URL: {self.base_url} API Key: {self.api_key}"

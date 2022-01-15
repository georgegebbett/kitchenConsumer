import json

from grocy import GrocyConfig

import requests


class GrocyRecipe:
    def __init__(self, id: int, grocy_config: GrocyConfig):
        self.name = None
        self.id = id
        self.grocy_config = grocy_config
        self.request_headers = {'GROCY-API-KEY': grocy_config.api_key}
        self.recipe_url = "/objects/recipes"

        self.get_recipe_details()

    def __repr__(self):
        return f"ID: {self.id} Name: {self.name}"

    def get_recipe_details(self):
        recipe_response = requests.get(
            f"{self.grocy_config.base_url}{self.recipe_url}?query[]=id={self.id}",
            headers=self.request_headers)

        recipe = json.loads(recipe_response.content)[0]
        self.name = recipe["name"]

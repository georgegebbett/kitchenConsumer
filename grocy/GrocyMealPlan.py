import json

from grocy import GrocyConfig
import requests
import datetime

from grocy.GrocyRecipe import GrocyRecipe


class GrocyMealPlan:

    def __init__(self, start_date_time: datetime.datetime, grocy_config: GrocyConfig):
        self.meal_plan = []

        self.start_date = start_date_time - datetime.timedelta(days=1)
        self.end_date = self.start_date + datetime.timedelta(days=8)
        self.grocy_config = grocy_config
        self.request_headers = {'GROCY-API-KEY': grocy_config.api_key}
        self.plan_url = "/objects/meal_plan"

        self.get_meal_plan()

    def get_meal_plan(self):

        print(f"{self.grocy_config.base_url}{self.plan_url}?query[]=day>{self.start_date.strftime('%Y-%m-%d')}&day<{self.end_date.strftime('%Y-%m-%d')}&limit=7")

        plan_response = requests.get(
            f"{self.grocy_config.base_url}{self.plan_url}?query[]=day>{self.start_date.strftime('%Y-%m-%d')}&query[]=day<{self.end_date.strftime('%Y-%m-%d')}&limit=7",
            headers=self.request_headers)

        meal_plan = json.loads(plan_response.content)
        # print(meal_plan)

        for meal in meal_plan:
            if meal['type'] == 'recipe':
                self.meal_plan.append({
                    'date': datetime.datetime.strptime(meal['day'], '%Y-%m-%d'),
                    'type': 'RECIPE',
                    'recipe': GrocyRecipe(meal['recipe_id'], self.grocy_config)
                })
            elif meal['type'] == 'note':
                self.meal_plan.append({
                    'date': datetime.datetime.strptime(meal['day'], '%Y-%m-%d'),
                    'type': 'NOTE',
                    'note': meal['note']
                })
            else:
                self.meal_plan.append({
                    'date': datetime.datetime.strptime(meal['day'], '%Y-%m-%d'),
                    'type': 'NOTE',
                    'note': "meal plan goes brrrrrrrrrr"
                })

def do_consume(item_id: int, quantity: int, grocy_config_object: grocy.GrocyConfig):
    headers = {'GROCY-API-KEY': grocy_config_object.api_key}
    consume_url = f"{grocy_config_object.base_url}/stock/products/{item_id}/consume"
    res = requests.post(consume_url, json={"amount": quantity}, headers=headers)
    print(res.json())

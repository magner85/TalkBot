import requests
import json

url = 'http://127.0.0.1:9900/new_lot'
with open("auc_data_349(Готовая продукция из наличия).json", encoding='utf-8-sig') as read_file:
    requests.post(url, json=json.load(read_file))

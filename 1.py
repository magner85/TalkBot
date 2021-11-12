import requests

url = 'http://127.0.0.1:9900/new_lot'
with open("auc_data_349(Готовая продукция из наличия).json", "r") as read_file:
    requests.post(url, data=read_file.read())

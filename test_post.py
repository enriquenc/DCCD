import requests

url = 'http://127.0.0.1:5001/transactions/new'
myobj = {'cargo_id': '123', 'private_key': '2ef99512e5b79d526282754338b3f25d7d5cf7e30dcf56b6300c0ffd59f8b875'}

x = requests.post(url, json = myobj)
print(x.content)
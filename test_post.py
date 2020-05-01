import requests
import json

url = 'http://127.0.0.1:5000/transactions/new'
myobj = {'serialized': '0123123123Fri May  1 22:54:08 2020046378707fa9dcd85d7618d5d0662ac8d1759ec6fb8340937a58a330b58d1fa17f7a3a9d58a51579a9e4fba913cb8231b4cc5136031eb78fa93132ea7f4f7ebee833368e9ccca802b18114755fa46927c3cb8342b7250ac9d1d4e78db438ea9f3753c06bc80541eb179d42595cf2d9423fdc2abfcc4f541dcc0da442ae9f8e7184'}

x = requests.post(url, json = myobj)
print(json.loads(x.content.decode('utf-8'))['result_code'])
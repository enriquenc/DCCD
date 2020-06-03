import sys
sys.path.append("../DCCD/")
import requests
import json
from objects import serializer
from crypto.wif import wifToPriv
from objects.transaction import Transaction

url = 'http://127.0.0.1:5100/transactions/new'

t = Transaction("134589037", '1588410854.301351', "25", "cargo_info")

private_key_wif = "5HpXfPm94cFqqZnQwZ5QnLrb4adRU9CrJXtxYWETxcnpWAPir61"
private_key = wifToPriv(private_key_wif)

t.sign(private_key)

obj = {'dictionary' : t.to_dictionary()}

x = requests.post(url, json = obj)
print(json.loads(x.content.decode('utf-8')))


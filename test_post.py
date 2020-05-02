import requests
import json

url = 'http://127.0.0.1:5000/transactions/new'
myobj = {'dictionary': {'cargo_id': '14324', 'timestamp': '1588410854.301351', 'public_key': '0404fb2416c38f8e0e4790973d6cfcae0bffd02db79f651ecba976f55e84406d49218d39cb1adee8a3a911ddfe0fae85491e990d48a8ce451224ab32143c8ac736', 'signed_hash': '654eae16817c3ebacd00c31b7d220d7b0f077acfea2ff087455d645a27f6d6706c92898f1ebbff6a8b1fcd33bc202e051438d46b304692a169a82cc38c449af8'}}
myobj = {'serialized': '00000143240001588410854.3013510404fb2416c38f8e0e4790973d6cfcae0bffd02db79f651ecba976f55e84406d49218d39cb1adee8a3a911ddfe0fae85491e990d48a8ce451224ab32143c8ac736654eae16817c3ebacd00c31b7d220d7b0f077acfea2ff087455d645a27f6d6706c92898f1ebbff6a8b1fcd33bc202e051438d46b304692a169a82cc38c449af8'}

x = requests.post(url, json = myobj)
print(json.loads(x.content.decode('utf-8')))
from serializer import Deserializer
from transaction import Transaction
import tx_validator
import requests
import json

from config import URL, NODE_PORT

def pending_pool(serialized):
	tx = None
	try:
		tx = Deserializer.deserialize(serialized)
	except:
		return
	if tx_validator.validate_transaction(tx) == False:
		return
	save_to_mempool(serialized)

def save_to_mempool(serialized):
	f = open('mempool', 'a+')
	f.write(serialized + '\n')
	f.close()

def take_transactions(count):
	f = open('mempool', 'r')
	lines = f.readlines()
	transaction_array = []
	for line in lines:
		transaction_array.append(line.rstrip())
	f.close()
	if count > 0 and count <= len(transaction_array):
		return (transaction_array[-count:])
	else:
		return transaction_array

from serializer import Deserializer
from transaction import Transaction
import tx_validator
import requests
import json
from file_system_wraper import FileSystem

from config import URL, NODE_PORT

def pending_pool(serialized):
	tx = None
	try:
		tx = Deserializer.deserialize(serialized)
		tx_validator.validate_transaction(tx)
	except Exception as msg:
		print("ERROR. Transaction wasn't added. " + str(msg))
		return
	FileSystem.addTransactionToMempool(serialized)

def take_transactions(count):
	transaction_array = FileSystem.getTransactionsFromMempool()

	if count > 0 and count <= len(transaction_array):
		return (transaction_array[-count:])
	else:
		return transaction_array

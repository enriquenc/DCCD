from serializer import Deserializer
import tx_validator
import requests
import json
import file_system_wraper

from config import URL, NODE_PORT

def pending_pool(serialized):
	tx = None
	try:
		tx = Deserializer.deserialize(serialized)
		tx_validator.validate_transaction(tx)
	except Exception as msg:
		print("ERROR. Transaction wasn't added. " + str(msg))
		return
	file_system_wraper.FileSystem.addTransactionToMempool(serialized)

def take_transactions(count):
	transaction_array = file_system_wraper.FileSystem.getTransactionsFromMempool()

	if count > 0 and count <= len(transaction_array):
		return (transaction_array[-count:])
	else:
		return transaction_array

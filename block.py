import merkle
import hashlib
import tx_validator
import serializer
import pending_pool
import time

class Block():

	def __init__(self, timestamp, previous_hash, transactions):
		self.timestamp = timestamp
		self.previous_hash = previous_hash
		self.transactions = transactions
		self.merkle_root = merkle.merkle_root(transactions)
		self.hash = self.calculate_hash()

	@classmethod
	def from_dict(cls, data):
		b = cls(data['timestamp'], data['previous_hash'], data['transaction'])
		b.hash = data['hash']
		b.merkle_root = data['merkle_root']
		return b

	def to_dictionary(self):
		return {
			'timestamp' : self.timestamp,
			'previous_hash' : self.previous_hash,
			'transactions' : self.transactions,
			'merkle_root' : self.merkle_root,
			'hash' : self.hash }

	def calculate_hash(self):
		return (hashlib.sha256((str(self.timestamp) + self.previous_hash + self.merkle_root).encode('utf-8')).hexdigest())

	def validate_transactions(self):
		# try:
		# 	if isinstance(self.transactions, list):
		# 		for i in self.transactions:
		# 			if self.transactions.index(i) == 0:
		# 				tx_validator.check_coinbase(pending_pool.make_obj(i))
		# 			continue
		# 		tx_validator.validation(pending_pool.make_obj(i))
		# 	else:
		# 		tx_validator.check_coinbase(pending_pool.make_obj(i))
		# except Exception as msg:
		# 	print(str(msg))
		# 	return False
		return True

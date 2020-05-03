import merkle
import hashlib
import tx_validator
from serializer import Deserializer
import time
import wallet
class Block():

	def __init__(self, timestamp, previous_hash, transactions):
		self.timestamp = timestamp
		self.previous_hash = previous_hash
		self.transactions = transactions
		self.merkle_root = merkle.merkle_root(transactions)
		self.hash = self.calculate_hash()
		self.public_key = None
		self.signed_hash = None
		#[!TODO] сделать обработку signed hash

	@classmethod
	def from_dict(cls, data):
		b = cls(data['timestamp'], data['previous_hash'], data['transactions'])
		b.merkle_root = data['merkle_root']
		b.hash = data['hash']
		b.public_key = data['public_key']
		b.signed_hash = data['signed_hash']
		return b

	def to_dictionary(self):
		return {
			'timestamp' : self.timestamp,
			'previous_hash' : self.previous_hash,
			'transactions' : self.transactions,
			'merkle_root' : self.merkle_root,
			'hash' : self.hash,
			'public_key' : self.public_key,
			'signed_hash' : self.signed_hash }

	def calculate_hash(self):
		return (hashlib.sha256((str(self.timestamp) + self.previous_hash + self.merkle_root).encode('utf-8')).hexdigest())

	def validate_transactions(self):
		for t in self.transactions:
			if tx_validator.validate_transaction(Deserializer.deserialize(t)) is False:
				return False
		return True

	def sign(self, private_key):
		sp = wallet.digital_signature(private_key, self.calculate_hash())
		self.signed_hash = sp[0]
		self.public_key = sp[1]


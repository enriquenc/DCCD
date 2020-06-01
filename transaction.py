import hashlib
import wallet
from time import asctime, gmtime
from serializer_config import NAN

class Transaction:
	def __init__(self, cargo_id, timestamp, temperature, information=NAN):
		self.cargo_id = cargo_id
		self.timestamp = timestamp
		self.temperature = temperature
		self.information = information
		self.public_key = None
		self.signed_hash = None

	@classmethod
	def from_dict(cls, d):
		obj = cls(d['cargo_id'], d['timestamp'], d['temperature'], d['information'])
		obj.public_key = d['public_key']
		obj.signed_hash = d['signed_hash']
		return obj

	def to_dictionary(self):
		return {'cargo_id' : self.cargo_id,
				'timestamp' : self.timestamp,
				'temperature' : self.temperature,
				'information' : self.information,
				'public_key' : self.public_key,
				'signed_hash' : self.signed_hash}

	def calculate_hash(self):
		concatenation = self.cargo_id + self.timestamp + self.temperature + self.information
		trn_hash = hashlib.sha256(concatenation.encode('utf-8')).hexdigest()
		return trn_hash

	def sign(self, private_key):
		sp = wallet.digital_signature(private_key, self.calculate_hash())
		self.signed_hash = sp[0]
		self.public_key = sp[1]


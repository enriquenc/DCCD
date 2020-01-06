
from serializer_config import *
from transaction import *

class Serializer:
	@staticmethod
	def serialize(tx):
		return ('0' * (CARGO_ID_LEN - len(tx.cargo_id)) + tx.cargo_id +
				(' ' * (TIMESTAMP_LEN - len(tx.timestamp))) + tx.timestamp +
				tx.public_key +
				tx.signed_hash)

class Deserializer:
	@staticmethod
	def deserialize(serialized):
		d = { "cargo_id": serialized[:CARGO_ID_LEN].lstrip("0"),
				"timestamp": serialized[CARGO_ID_LEN:(CARGO_ID_LEN + TIMESTAMP_LEN)],
				"public_key": serialized[(CARGO_ID_LEN + TIMESTAMP_LEN):(CARGO_ID_LEN + TIMESTAMP_LEN + PUBLIC_KEY_LEN)],
				"signed_hash": serialized[(CARGO_ID_LEN + TIMESTAMP_LEN + PUBLIC_KEY_LEN):] }
		tx = Transaction(d['cargo_id'], d['timestamp'])
		tx.public_key = d['public_key']
		tx.signed_hash = d['signed_hash']
		return tx

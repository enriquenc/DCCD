
from serializer_config import *
from transaction import *

class Serializer:
	@staticmethod
	def serialize(tx):
		information_serialized = ""

		if tx.information != NAN:
			information_serialized = "0" * (INFROMATION_LEN - len(tx.information)) + tx.information
		else:
			information_serialized = tx.information

		return ('0' * (CARGO_ID_LEN - len(tx.cargo_id)) + tx.cargo_id +
				('0' * (TIMESTAMP_LEN - len(tx.timestamp))) + tx.timestamp +
				('0' * (TEMPERATURE_LEN - len(tx.temperature)) + tx.temperature) +
				information_serialized +
				tx.public_key +
				tx.signed_hash)

class Deserializer:
	@staticmethod
	def deserialize(serialized):
		information_length = 0
		if serialized[CARGO_ID_LEN + TIMESTAMP_LEN + TEMPERATURE_LEN: CARGO_ID_LEN +
				TIMESTAMP_LEN + TEMPERATURE_LEN + len(NAN)] == NAN:
			information_length = len(NAN)
		else:
			information_length = INFROMATION_LEN
		d = { "cargo_id": serialized[:CARGO_ID_LEN].lstrip("0"),
				"timestamp": serialized[CARGO_ID_LEN:(CARGO_ID_LEN + TIMESTAMP_LEN)].lstrip("0"),
				"temperature" : serialized[CARGO_ID_LEN + TIMESTAMP_LEN :
							CARGO_ID_LEN + TIMESTAMP_LEN + TEMPERATURE_LEN].lstrip("0"),
				"information" : serialized[CARGO_ID_LEN + TIMESTAMP_LEN + TEMPERATURE_LEN :
							CARGO_ID_LEN + TIMESTAMP_LEN + TEMPERATURE_LEN + information_length].lstrip("0"),
				"public_key": serialized[(CARGO_ID_LEN + TIMESTAMP_LEN + TEMPERATURE_LEN + information_length):
							(CARGO_ID_LEN + TIMESTAMP_LEN + TEMPERATURE_LEN + information_length + PUBLIC_KEY_LEN)],
				"signed_hash": serialized[(CARGO_ID_LEN + TIMESTAMP_LEN + TEMPERATURE_LEN + information_length + PUBLIC_KEY_LEN):] }
		return Transaction.from_dict(d)


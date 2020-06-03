import unittest
import sys
sys.path.append("../DCCD/")
from objects.serializer import *
from objects.transaction import *


#data for serialization tests
data = ["1234567890", "123123123123", "36", "information"]
private_key = "1cee98bfe1bf08cea121b62145aa8ad0ac8f5b2543affc8c9bc38074eea21b10"
tx_before = Transaction(data[0], data[1], data[2], data[3])
tx_before.sign(private_key)
s = Serializer.serialize(tx_before)
tx_after = Deserializer.deserialize(s)
#data for transaction dict tests
dict_org = tx_before.to_dictionary()
obj_from_dict = Transaction.from_dict(dict_org)

class TestAll(unittest.TestCase):

	def test_serialization_cargo_id(self):
		self.assertEqual(tx_before.cargo_id, tx_after.cargo_id)

	def test_serialization_timestamp(self):
		self.assertEqual(tx_before.timestamp, tx_after.timestamp)

	def test_serialization_public_key(self):
		self.assertEqual(tx_before.public_key, tx_after.public_key)

	def test_serialization_signed_hash(self):
		self.assertEqual(tx_before.signed_hash, tx_after.signed_hash)

	def test_transaction_from_dict_cargo_id(self):
		self.assertEqual(tx_before.cargo_id, obj_from_dict.cargo_id)

	def test_transaction_from_dict_timestamp(self):
		self.assertEqual(tx_before.timestamp, obj_from_dict.timestamp)

	def test_transaction_from_dict_public_key(self):
		self.assertEqual(tx_before.public_key, obj_from_dict.public_key)

	def test_transaction_from_dict_signed_hash(self):
		self.assertEqual(tx_before.signed_hash, obj_from_dict.signed_hash)




if __name__ == '__main__':
	unittest.main()
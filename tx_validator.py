import transaction
import re
import wallet

def validate_transaction(t):
	if t == None:
		print('Invalid transaction')
		return
	check_digital_signature(t)


def check_digital_signature(t):
	assert wallet.sign_verify(t.signed_hash, t.public_key, t.calculate_hash()), "Invalid digital signature of transaction."

def validate_coinbase(t):
	# try:
	# 	assert t.sender == "0" * 34, 'Invalid coinbase transaction'
	# 	check_address(t.recipient)
	# 	check_sender_address(t.recipient, t.public_key)
	# 	check_validity(t)
	# except Exception as msg:
	# 	print(str(msg))
	# 	return False
	return True

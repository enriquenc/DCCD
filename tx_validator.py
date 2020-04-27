import wallet
from serializer_config import CARGO_ID_LEN, TIMESTAMP_LEN
from file_system_wraper import FileSystem

def validate_transaction(t):
	assert t, 'Invalid transaction'
	assert t.public_key in FileSystem.getPermissionedCheckpointsPublicAddresses(), 'Invalid checkpoint address'
	check_digital_signature(t)

def check_digital_signature(t):
	assert wallet.sign_verify(t.signed_hash, t.public_key, t.calculate_hash()), "Invalid digital signature of transaction."

def validate_coinbase(t):
	assert t, 'Invalid transaction'
	assert t.cargo_id == "0" * CARGO_ID_LEN, 'Invalid coinbase transaction cargo_id'
	assert t.timestamp == "0" * TIMESTAMP_LEN, 'Invalid coinbase transaction timestamp'
	assert t.public_key in FileSystem.getPermissionedValidatorsPublicAddresses(), 'Invalid validator address'
	check_digital_signature(t)


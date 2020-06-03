from crypto import signature
from objects.serializer_config import CARGO_ID_LEN, TIMESTAMP_LEN
from wrapers.file_system_wraper import FileSystem
from objects.return_code import ReturnCode

def validate_transaction(t):
	if t is None:
		return ReturnCode.INVALID_TRANSACTION
	if check_transactions_permissions(t) is False:
		return ReturnCode.UNAUTHORIZED_PRIVATE_KEY
	if check_digital_signature(t) is False:
		return ReturnCode.INVALID_SIGNATURE
	return ReturnCode.OK

def check_digital_signature(t):
	return signature.sign_verify(t.signed_hash, t.public_key, t.calculate_hash())

def check_transactions_permissions(t):
	return t.public_key in FileSystem.getPermissionedCheckpointsPublicAddresses()


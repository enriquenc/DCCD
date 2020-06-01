import merkle
import wallet
from file_system_wraper import FileSystem
from return_code import ReturnCode

def validate(block):
	if block is None:
		return ReturnCode.INVALID_BLOCK
	if check_block_creation_permissions(block) is False:
		return ReturnCode.UNAUTHORIZED_PRIVATE_KEY
	if check_merkle_root(block) is False:
		return ReturnCode.INVALID_MERKLE_ROOT
	if check_digital_signature(block) is False:
		return ReturnCode.INVALID_SIGNATURE
	if check_block_hash(block) is False:
		return ReturnCode.INVALID_BLOCK_HASH
	return ReturnCode.OK

def check_merkle_root(block):
	return merkle.merkle_root(block.transactions) == block.merkle_root

def check_block_hash(block):
	return block.hash == block.calculate_hash()

def check_digital_signature(block):
	return wallet.sign_verify(block.signed_hash, block.public_key, block.calculate_hash())

def check_block_creation_permissions(t):
	return t.public_key in FileSystem.getPermissionedValidatorsPublicAddresses()


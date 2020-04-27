import block
import merkle
import time
import hashlib
import tx_validator
import pending_pool

def validate(block):
	assert merkle.merkle_root(block.transactions) == block.merkle_root, "Invlalid Merkle Root of transactions."
	assert block.hash == block.calculate_hash(), "Invalid hash of block."
	assert time.time() > float(block.timestamp), "Invalid timestamp"


import wallet
import os
import re


files = ['keys/TEST_checkpoints_private_keys', 'keys/TEST_validators_private_keys']

for fname in files:
	pubkeys = []

	with open(fname, 'r') as f:
		keys = f.read().splitlines()
		for key in keys:
			pubkeys.append(wallet.privToPub(key))

	with open(re.sub("private", "public", fname[5:]), 'w') as f:
		for line in pubkeys:
			f.write(line + '\n')


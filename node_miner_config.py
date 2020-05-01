import wallet
import color_output
MINER_PRIVATE_KEY = None

try:
	with open('node_keys/validator_private_key.wif', 'r') as f:
		MINER_PRIVATE_KEY = wallet.wifToPriv(f.readline().rstrip())
except:
	print(color_output.prRed('No validator_private_key.wif file.\n'
			'Create it and add permissioned private key in wif format to mine the blocks.\n'))

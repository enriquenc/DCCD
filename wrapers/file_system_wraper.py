
import json
import sys
from objects import block
from node_config.path_config import CONFIG_PATH, WRITE_PATH
from staff import color_output

class FileSystem():
	@staticmethod
	def addTransactionToMempool(serialized):
		with open(WRITE_PATH + 'mempool', 'a+') as f:
			f.write(serialized + '\n')

	@staticmethod
	def removeTransactionFromMempool(serialized):
		data = FileSystem.getTransactionsFromMempool()
		data.remove(serialized)
		# WTF FIX IT
		with open(WRITE_PATH + 'mempool', 'w') as f:
			f.write('\n'.join(data))


	@staticmethod
	def getTransactionsFromMempool():
		try:
			with open(WRITE_PATH + 'mempool', 'r') as f:
				return f.read().splitlines()
		except:
			return []

	@staticmethod
	def addNode(port):
		with open(CONFIG_PATH + 'friendly_nodes.config', 'a+') as f:
			f.write(port + '\n')

	@staticmethod
	def getNodes():
		with open(CONFIG_PATH + 'friendly_nodes.config', 'r') as f:
			return f.read().splitlines()


	@staticmethod
	def addNewBlock(block, index):
		with open(WRITE_PATH + '%04d' % index + '.block', 'w') as outfile:
			json.dump(block.to_dictionary(), outfile)

	@staticmethod
	def getBlocksList():
		block_list = []
		try:
			i = 0
			while True:
				with open(WRITE_PATH + '%04d' % i + '.block') as json_file:
					data = json.load(json_file)
					block_list.append(block.Block.from_dict(data))
				i = i + 1
		except:
			pass
		return block_list

	@staticmethod
	def getPermissionedValidatorsPublicAddresses():
		with open(CONFIG_PATH + 'permissioned_keys/validators_public_keys', 'r') as f:
			return f.read().splitlines()

	@staticmethod
	def getPermissionedCheckpointsPublicAddresses():
		with open(CONFIG_PATH + 'permissioned_keys/checkpoints_public_keys', 'r') as f:
			return f.read().splitlines()

	@staticmethod
	def getNodeWifPrivateKey():
		try:
			with open(CONFIG_PATH + '/node_keys/validator_private_key.wif', 'r') as f:
				return f.readline().rstrip()
		except:
			print(color_output.prRed('No validator_private_key.wif file.'))
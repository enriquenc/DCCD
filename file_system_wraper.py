
import json
from block import Block

class FileSystem():
	@staticmethod
	def addTransactionToMempool(serialized):
		with open('mempool', 'a+') as f:
			f.write(serialized + '\n')

	@staticmethod
	def getTransactionsFromMempool():
		with open('mempool', 'r') as f:
			return f.read().splitlines()

	@staticmethod
	def addNode(port):
		with open('nodes.config', 'a+') as f:
			f.write(port + '\n')

	@staticmethod
	def getNodes():
		with open('nodes.config', 'r') as f:
			return f.read().splitlines()


	@staticmethod
	def addNewBlock(block, index):
		with open('blocks/' + '%04d' % index + '.block', 'w') as outfile:
			json.dump(block.to_dictionary(), outfile)

	@staticmethod
	def getBlocksList():
		block_list = []
		try:
			i = 0
			while True:
				with open('blocks/' + '%04d' % i + '.block') as json_file:
					data = json.load(json_file)
					block_list.append(Block.from_dict(data))
				i = i + 1
		except:
			pass
		return block_list

	@staticmethod
	def getPermissionedValidatorsPublicAddresses():
		with open('validators_public_keys', 'r') as f:
			return f.read().splitlines()

	@staticmethod
	def getPermissionedCheckpointsPublicAddresses():
		with open('checkpoints_public_keys', 'r') as f:
			return f.read().splitlines()

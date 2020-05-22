
import json
import block
from path_config import PATH

class FileSystem():
	@staticmethod
	def addTransactionToMempool(serialized):
		with open(PATH + 'mempool', 'a+') as f:
			f.write(serialized + '\n')

	@staticmethod
	def removeTransactionFromMempool(serialized):
		data = FileSystem.getTransactionsFromMempool()
		data.remove(serialized)
		with open(PATH + 'mempool', 'w') as f:
			f.write('\n'.join(data))


	@staticmethod
	def getTransactionsFromMempool():
		with open(PATH + 'mempool', 'r') as f:
			return f.read().splitlines()

	@staticmethod
	def addNode(port):
		with open(PATH + 'nodes.config', 'a+') as f:
			f.write(port + '\n')

	@staticmethod
	def getNodes():
		with open(PATH + 'nodes.config', 'r') as f:
			return f.read().splitlines()


	@staticmethod
	def addNewBlock(block, index):
		with open(PATH + 'blocks/' + '%04d' % index + '.block', 'w') as outfile:
			json.dump(block.to_dictionary(), outfile)

	@staticmethod
	def getBlocksList():
		block_list = []
		try:
			i = 0
			while True:
				with open(PATH + 'blocks/' + '%04d' % i + '.block') as json_file:
					data = json.load(json_file)
					block_list.append(block.Block.from_dict(data))
				i = i + 1
		except:
			pass
		return block_list

	@staticmethod
	def getPermissionedValidatorsPublicAddresses():
		with open(PATH + 'keys/validators_public_keys', 'r') as f:
			return f.read().splitlines()

	@staticmethod
	def getPermissionedCheckpointsPublicAddresses():
		# По хорошему, нужно считывать только один раз во время
		# инициализации узла и после этого сохранять в основном классе
		# блокчейна, предварительно проверив, что дружественные ноды
		# тоже поддерживают эти же ключи.
		with open(PATH + 'keys/checkpoints_public_keys', 'r') as f:
			return f.read().splitlines()

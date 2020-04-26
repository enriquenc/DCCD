
import json
from block import Block

class FileSystem():
	@staticmethod
	def addNode(port):
		f = open('nodes.config', 'a+')
		f.write(port + '\n')
		f.close()

	@staticmethod
	def getNodes():
		f = open('nodes.config', 'r')
		nodes = f.readlines()
		f.close()
		for i in range(len(nodes)):
			nodes[i] = nodes[i].rstrip()
		return nodes

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

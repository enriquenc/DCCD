import time
import block
import json
from flask import Flask
from flask import request
import tx_validator
import requests
import block_validator
import api_wraper
from file_system_wraper import FileSystem
class Blockchain:

	def __init__(self, URL, node_port):
		self.url = URL
		self.node_port = str(node_port)

		self.chain = self.get_my_chain()
		self.friendly_nodes = []
		self.get_friendly_nodes()
		self.miner_queue_number = None

	def new_block(self, block):
		self.chain.append(block)
		FileSystem.addNewBlock(block, self.chain.index(block))

	def find_miner_queue_number(self):
		queue = api_wraper.get_miner_queue_number_list(self.url, self.friendly_nodes)
		for num in range(len(queue)):
			if num in queue or str(num) in queue:
				continue
			return num
		return len(queue)

	def to_dictionary(self):
		block_dict_list = []
		for block in self.chain:
			block_dict_list.append(block.to_dictionary())
		return block_dict_list

	def mine(self, block):
		#self.miner_queue_number = api_wraper.get_miner_queue_number_list(self.url, self.friendly_nodes)
		# Спрашиваем очередь у соседей, если очередь наша, то добавляем блок
		# и рассказываем всем соседям.
		# if self.resolve_conflicts() == False:
		# 	"""нужно вернуть транзакции в пул"""
		# 	return
		self.new_block(block)
		# requests.post(self.url + self.node_port + '/newblock', json = block.to_dictionary())
		return True

	def get_my_chain(self):
		# [!TODO] In future we shouldn't store all chain in ROM.
		self.chain = FileSystem.getBlocksList()
		return self.chain

	def get_friendly_nodes(self):
		if self.friendly_nodes == []:
			self.friendly_nodes = FileSystem.getNodes()
			if self.friendly_nodes == []:
				print("You don't have friendly nodes.")
		return self.friendly_nodes

	def resolve_conflicts(self):
		longest_chain_node = None
		longest_chain_length = 0
		d = None
		for node in self.friendly_nodes:
			try:
				d = requests.get(self.url + node + '/chain/length').json()
			except:
				print('\nNode with port ' + node + ' is inactive.')
				continue
			node_chain_length = d['length']
			if  node_chain_length > longest_chain_length:
				longest_chain_node = node
				longest_chain_length = node_chain_length

		d = requests.get(self.url + self.node_port + '/chain/length').json()
		my_length = d['length']

		print("\nPort of node with longest chain: " + str(longest_chain_node))
		print("Longest peer node chain: " + str(longest_chain_length))
		print("Length of your chain: " + str(my_length), end='\n\n')

		if (longest_chain_length > my_length):
			new_chain = requests.get(self.url + longest_chain_node + '/chain').content
			d = json.loads(new_chain.decode('utf-8'))
			new = d.to_dictionary()
			f = new.copy()
			try:
				self.is_valid_chain(f)
			except Exception as msg:
				print(str(msg))
				'''тут удаление ноды с невалидным блокчейном'''
				'''тут вызов resolve_conflicts еще раз'''
				return
			count_conflict_blocks = 0
			while count_conflict_blocks < len(self.chain):
				if self.chain[count_conflict_blocks].hash != new[count_conflict_blocks].hash:
					break
				count_conflict_blocks = count_conflict_blocks + 1
			self.chain = new
			self.write_chain(count_conflict_blocks)
			print('Conflicts resolved. Your blockchain is updated')
			print("Length of your chain: " + str(len(self.chain)), end='\n\n')
			return False
		print('No conflicts.')
		return True

	def write_chain(self, start_id):
		i = start_id
		while i < len(self.chain):
			self.new_block(self.chain[i])
			i = i + 1

	def is_valid_chain(self, chain):
		prev = block.Block('1', '1', '1')
		prev.hash = '0' * 64
		# [!TODO] Проверить правильные ли хеши вообще
		for b in chain:
			block_validator.validate(b)
			if prev != None:
				if prev.hash != b.previous_hash:
					return False
			prev = b
		return True


	def add_node(self, node):
		self.friendly_nodes.append(node)
		FileSystem.addNode(node)
		print('Node with port ' + node + ' added.')

	def genesis_block(self, transactions):
		gb = block.Block(str(time.time()), '0' * 64, transactions)
		return gb

	def tostr(self):
		print('#' * 100)
		for nd in self.chain:
			print(nd.previous_hash, end="")
			print(' -> ', end="")
			print(nd.hash)
		print('#' * 100)
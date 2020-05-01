import time
import json
from flask import Flask
from flask import request
from multiprocessing import Process, Pipe
from blockchain import Blockchain
from block import Block
import tx_validator
import requests
import pending_pool
import block_validator
import sys
import wallet
import transaction
import serializer
from flask_cors import CORS
from serializer import *
from file_system_wraper import FileSystem
from serializer_config import CARGO_ID_LEN
from config import URL, NODE_PORT
from enum import Enum
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from node_miner_config import MINER_PRIVATE_KEY
class ReturnCode(Enum):
	OK = 0
	WRONG_PARAMETER = 1
	UNAUTHORIZED_PRIVATE_KEY = 2

MAX_BLOCK_TRANSACTIONS = 3

node = Flask(__name__)
CORS(node)

blockchain = Blockchain(URL, NODE_PORT)

def miner_start_check_get_transaction():
	transactions = FileSystem.getTransactionsFromMempool()
	if len(transactions) > MAX_BLOCK_TRANSACTIONS:
		transactions = transactions[:MAX_BLOCK_TRANSACTIONS]

	for tx in transactions:
		try:
			tx_validator.validate_transaction(serializer.Deserializer.deserialize(tx))
		except:
			transactions.remove(tx)
			FileSystem.removeTransactionFromMempool(tx)
			print('Error transaction. Removed from mempool')
			continue

	if transactions == []:
		print('Mempool is emtpy.')
		return False

	if MINER_PRIVATE_KEY is None:
		print('No node miner private key.')
		return False
	try:
		if wallet.privToPub(MINER_PRIVATE_KEY) not in FileSystem.getPermissionedValidatorsPublicAddresses():
			print('Unpermissioned node miner private key.')
			return False
	except:
		print('Incorrect node miner private key.')
		return False
	return transactions

def main_node_block_miner():
	global blockchain
	transactions = miner_start_check_get_transaction()
	if transactions is False:
		return
	b = None
	if blockchain.chain == []:
		b = blockchain.genesis_block(transactions)
	else:
		b = Block(time.time(), blockchain.chain[-1].hash, transactions)
	if blockchain.mine(b) is True:
		for t in transactions:
			FileSystem.removeTransactionFromMempool(t)
		print(b.hash)


scheduler = BackgroundScheduler()
scheduler.add_job(func=main_node_block_miner, trigger="interval", seconds=3)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def get_return_value(code, data=[]):
	result = {'result_code': code,
				'data': data}
	return json.dumps(result)

@node.route('/miner/queue/number', methods=['GET'])
def get_miner_queue_number():
	global blockchain
	return json.dumps(blockchain.miner_queue_number)

@node.route('/newblock', methods=['POST'])
def new_block():
	global blockchain
	block = Block.from_dict(request.get_json())
	try:
		block_validator.validate(block)
	except Exception as msg:
		print("ERROR. Block wasn't added. " + str(msg))
		return 1
	blockchain.new_block(block)
	return 0

@node.route('/addnode', methods=['POST'])
def add_node():
	port = request.get_json()['port']
	blockchain.add_node(port)
	return 0

@node.route('/transactions/pendings')
def get_pending_thxs():
	return json.dumps(pending_pool.take_transactions(0))


@node.route('/chain')
def get_chain():
	global blockchain
	return json.dumps(blockchain.to_dictionary())

@node.route('/chain/length')
def get_chain_length():
	global blockchain
	return json.dumps(len(blockchain.chain))

@node.route('/nodes')
def get_nodes():
	global blockchain
	return json.dumps(blockchain.get_friendly_nodes())


@node.route('/block/', methods=['GET'])
def get_n_block():
	global blockchain
	height = int(request.args.get('height'))

	if height >= len(blockchain.chain):
		return -1

	return json.dumps(blockchain.chain[height].to_dictionary())

@node.route('/block/last')
def get_last_block():
	global blockchain
	return json.dumps(blockchain.chain[-1].to_dictionary())


@node.route('/transactions/new', methods=['POST'])
def new_transaction():
	serialized = request.get_json()['serialized']
	trn = serializer.Deserializer.deserialize(serialized)
	print(trn.public_key)
	if trn.public_key not in FileSystem.getPermissionedCheckpointsPublicAddresses():
		return get_return_value(ReturnCode.UNAUTHORIZED_PRIVATE_KEY.value)
	tx_validator.validate_transaction(trn)
	pending_pool.pending_pool(serialized)
	return get_return_value(ReturnCode.OK.value)


@node.route('/find/', methods=['GET'])
def get_info_by_cargo_id():
	param = request.args.get('cargo_id')
	data = []
	if param is not None:
		chain = blockchain.get_my_chain()
		for block in chain:
			for tx in block.transactions:
				tx_obj = Deserializer.deserialize(tx)
				if tx_obj.cargo_id == param:
					data.append(tx_obj.to_dictionary())
	if data == []:
		return get_return_value(ReturnCode.WRONG_PARAMETER.value)
	return get_return_value(ReturnCode.OK.value, data)

@node.route('/')
def get_hello():
	return json.dumps("HELLO DCCD")


if __name__ == '__main__':
	p2 = Process(target = node.run(port = NODE_PORT))
	p2.start()



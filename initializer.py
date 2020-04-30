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
#import miner_cli
from flask_cors import CORS
from serializer import *
from file_system_wraper import FileSystem
from serializer_config import CARGO_ID_LEN

from config import URL, NODE_PORT

from enum import Enum
class ReturnCode(Enum):
	OK = 0
	WRONG_PARAMETER = 1
	UNAUTHORIZED_PRIVATE_KEY = 2

node = Flask(__name__)
CORS(node)

blockchain = Blockchain(URL, NODE_PORT)



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
	# [!TODO] Подпись транзакции на стороне клиента (Обязательно!)
	param = request.get_json()
	# will be done on the client
	cargo_id = param['cargo_id']
	private_key = param['private_key']
	trn = transaction.Transaction(cargo_id, asctime(gmtime()))
	trn.sign(private_key)
	serialized = serializer.Serializer.serialize(trn)
	##############################
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



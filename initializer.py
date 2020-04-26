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

from config import URL, NODE_PORT

node = Flask(__name__)
CORS(node)

blockchain = Blockchain(URL, NODE_PORT)

@node.route('/miner/queue/number', methods=['GET'])
def get_miner_queue_number():
	global blockchain
	return json.dumps(blockchain.miner_queue_number)

@node.route('/newblock', methods=['POST'])
def new_block():
	global blockchain
	block = Block.from_dict(request.get_json())
	if block_validator.validate(block) is False:
		return -1
	blockchain.new_block(block)
	"[TODO] Remove transactions from mempool"
	return 0

@node.route('/addnode', methods=['POST'])
def add_node():
	port = request.get_json()['port']
	blockchain.add_node(port)
	return 0

@node.route('/transactions/new', methods=['POST'])
def submit_tx():
	"[TODO] send to all nodes"
	pending_pool.pending_pool(request.get_json()['serialized'])
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


@node.route('/front/transtaction/new', methods=['POST', 'OPTIONS'])
def get_front_new_transaction():
	# [!TODO] Подпись транзакции на стороне клиента (Обязательно!)
	data = request.get_json()
	cargo_id = data['cargo_id']
	private_key = data['private_key']
	trn = transaction.Transaction(cargo_id, asctime(gmtime()))
	trn.sign(private_key)
	tx_validator.validation(trn)
	print(serializer.Serializer.serialize(trn))
	return 0

@node.route('/front/find/cargoid', methods=['GET'])
def get_info_by_cargo_id():
	res = ['1231231231Fri Apr 17 20:53:21 202004663ccdca6dd5eb02265a827613c3c0e6af1e6bb588f4c1e4d336d5bae8c3b49c496aa3eb938f1b2de36278705fb91d1e4e74f9f48f079b38874b49dcb706527c9ebb5f263bf6ce39ca71ca551569f8579fd70a91c9895eb660deb4694dae13e550b8a7481883e9120763b2404c267e7e53fc3e33f78e17fa85ce425d847dd13a',
			'1231231231Fri Apr 17 20:54:53 2020048b31d50b06d6bd85e4363576d29e003b954b829bbb6695fceb6f3159300e7600bd58b7a33e3f630b3fdb25fa5eb956490f1a8b1b1de8cf2e4bfb0a817c19f5dba4f234b3ccafbe0ad4ac8988185e89cc44c73c934913b6901486271a3555025a5c652a5f6af317e453ed63e8e37f1a262df6fa02077589a9864a5a6ba2e288e9',
			'1231231231Fri Apr 17 20:55:49 20200433ebc82f5a60861a4a17bb338a4669f025d780f519a6ed00bff82e89bd7f272db0e7a5b4a0b8e7a32da823f43e70f69334d50be61a8fcda102e19c801a8e2c3f77b76a38669e05fef57f427fb5ec3d45266ee9188f94de3e4ee515fe697156ee6f5469c618e95e9161d5a840f205d229e56303b277e07d5f2d0575b031bd63e9']
	objs = []
	for t in res:
		temp = Deserializer.deserialize(t)
		objs.append(temp.to_dictionary())
	cargo_id = request.args.get('cargo_id')
	return json.dumps(objs)

@node.route('/')
def get_hello():
	return json.dumps("HELLO DCCD")


if __name__ == '__main__':
	p2 = Process(target = node.run(port = NODE_PORT))
	p2.start()



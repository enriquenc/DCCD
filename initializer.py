import time
import json
from flask import Flask, render_template, request
from multiprocessing import Process, Pipe
from blockchain import Blockchain
from block import Block
import tx_validator
import block_validator
import sys
import wallet
from serializer import Deserializer, Serializer
from flask_cors import CORS
from file_system_wraper import FileSystem
from serializer_config import CARGO_ID_LEN
from config import URL, NODE_PORT
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from node_miner_config import MINER_PRIVATE_KEY
import color_output
from return_code import ReturnCode

MAX_BLOCK_TRANSACTIONS = 3
MINING_INTERVAL_SECONDS = 3

def run():
	node = Flask(__name__)
	CORS(node)
	return node

node = run()
blockchain = Blockchain(URL, NODE_PORT)

def miner_start_check_get_transaction():
	transactions = FileSystem.getTransactionsFromMempool()
	if len(transactions) > MAX_BLOCK_TRANSACTIONS:
		transactions = transactions[:MAX_BLOCK_TRANSACTIONS]

	for tx in transactions:
		if tx_validator.validate_transaction(Deserializer.deserialize(tx)) != ReturnCode.OK:
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
	b.sign(MINER_PRIVATE_KEY)
	if blockchain.mine(b) is True:
		# подпись транзакции
		for t in transactions:
			FileSystem.removeTransactionFromMempool(t)
		# Рассказываю тут всем дружественным нодам о то что я смайнил новый блок
		print(b.hash)


scheduler = BackgroundScheduler()
scheduler.add_job(func=main_node_block_miner, trigger="interval", seconds=MINING_INTERVAL_SECONDS)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def get_return_value(code, data=[]):
	result = {'result_code': code,
				'data': data}
	return json.dumps(result)

@node.route('/miner/queue/number', methods=['GET'])
def get_miner_queue_number():
	return get_return_value(ReturnCode.OK.value, blockchain.miner_queue_number)

@node.route('/newblock', methods=['POST'])
def new_block():
	block = None
	try:
		block = Block.from_dict(request.get_json())
	except Exception as msg:
		print("ERROR. Block wasn't added. " + str(msg))
		return get_return_value(ReturnCode.INVALID_ARGUMENT)
	if block.validate_transactions() is False:
		return get_return_value(ReturnCode.INVALID_ARGUMENT)
	blockchain.new_block(block)
	return get_return_value(ReturnCode.OK.value)

@node.route('/addnode', methods=['POST'])
def add_node():
	port = request.get_json()['port']
	blockchain.add_node(port)
	return get_return_value(ReturnCode.OK.value)

@node.route('/nodes', methods=['GET'])
def get_nodes():
	return get_return_value(ReturnCode.OK.value, blockchain.get_friendly_nodes())


@node.route('/transactions/pendings', methods=['GET'])
def get_pending_thxs():
	return get_return_value(ReturnCode.OK.value, FileSystem.getTransactionsFromMempool())

@node.route('/chain', methods=['GET'])
def get_chain():
	try:
		height = int(request.args.get('height'))
		assert height
	except:
		return get_return_value(ReturnCode.INVALID_ARGUMENT.value)
	chain = blockchain.get_full_chain()
	if chain == []:
		return get_return_value(ReturnCode.EMPTY_CHAIN.value)
	if height > len(chain):
		return get_return_value(ReturnCode.WRONG_CHAIN_HEIGHT_NUMBER.value)
	return get_return_value(ReturnCode.OK.value, blockchain.to_dictionary(chain[-height:]))

@node.route('/chain/length', methods=['GET'])
def get_chain_length():
	chain = blockchain.get_full_chain()
	return get_return_value(ReturnCode.OK.value, len(chain))


@node.route('/transactions/new', methods=['POST'])
def new_transaction():
	serialized_tx = None
	dictionary_tx = None
	tx = None
	try:
		serialized_tx = request.get_json()['serialized']
		tx = Deserializer.deserialize(serialized_tx)
	except:
		try:
			dictionary_tx = request.get_json()['dictionary']
			tx = Transaction.from_dict(dictionary_tx)
		except:
			return get_return_value(ReturnCode.INVALID_ARGUMENT.value)

	code = tx_validator.validate_transaction(tx)
	if code.value != ReturnCode.OK.value:
		print("ERROR. Transaction wasn't added. " + color_output.prRed(code.name))
		return get_return_value(code.value)
	FileSystem.addTransactionToMempool(Serializer.serialize(tx))
	return get_return_value(ReturnCode.OK.value)


def get_transactions_by_cargo_id(cargo_id):
	data = []
	chain = blockchain.get_full_chain()
	for block in chain:
		for tx in block.transactions:
			tx_obj = Deserializer.deserialize(tx)
			if tx_obj.cargo_id == cargo_id:
				data.append(tx_obj.to_dictionary())
	if data == []:
		return get_return_value(ReturnCode.CARGO_ID_NOT_FOUND.value)
	return get_return_value(ReturnCode.OK.value, data)

def get_block_by_height(height):
	chain = blockchain.get_full_chain()
	if chain == []:
		return get_return_value(ReturnCode.EMPTY_CHAIN.value)
	if height >= len(chain):
		return get_return_value(ReturnCode.WRONG_CHAIN_HEIGHT_NUMBER.value)
	return get_return_value(ReturnCode.OK.value, chain[height].to_dictionary())

@node.route('/find/', methods=['GET'])
def find():
	param = request.args.get('cargo_id')
	if param is not None:
		return get_transactions_by_cargo_id(param)
	param = request.args.get('block_by_height')
	if param is not None:
		return get_block_by_height(param)
	return get_return_value(ReturnCode.INVALID_ARGUMENT.value)

@node.route('/')
def get_hello():
	return render_template('index.html')

@node.route('/reader', methods=['POST'])
def get_reader_data():
	print(request.get_json())
	return 'ok'




# if __name__ == '__main__':
# 	run()


import time
import json
from flask import Flask, render_template, request
from multiprocessing import Process, Pipe
from objects.blockchain import Blockchain
from objects.block import Block
from validators import tx_validator
from validators import block_validator
import sys
from crypto import signature
from objects.serializer import Deserializer, Serializer
from flask_cors import CORS
from objects.serializer_config import CARGO_ID_LEN, NAN
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from staff import color_output
from objects.return_code import ReturnCode
from objects.transaction import Transaction
from crypto.wif import wifToPriv
from wrapers.file_system_wraper import FileSystem

MINER_PRIVATE_KEY = wifToPriv(FileSystem.getNodeWifPrivateKey().rstrip())

MAX_BLOCK_TRANSACTIONS = 3
MINING_INTERVAL_SECONDS = 3

app = Flask(__name__)
CORS(app)

blockchain = Blockchain()

def miner_start_check_get_transaction():
	transactions = FileSystem.getTransactionsFromMempool()
	if len(transactions) > MAX_BLOCK_TRANSACTIONS:
		transactions = transactions[:MAX_BLOCK_TRANSACTIONS]

	for tx in transactions:
		code = tx_validator.validate_transaction(Deserializer.deserialize(tx))
		if code != ReturnCode.OK:
			transactions.remove(tx)
			FileSystem.removeTransactionFromMempool(tx)
			print('Error transaction. Removed from mempool, ' + color_output.prRed(code.name))
			continue

	if transactions == []:
		print('Mempool is emtpy.')
		return False

	if MINER_PRIVATE_KEY is None:
		print('No node miner private key.')
		return False
	try:
		if signature.privToPub(MINER_PRIVATE_KEY) not in FileSystem.getPermissionedValidatorsPublicAddresses():
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
		if block_validator.validate(b) != ReturnCode.OK:
			print("pezda")
			return
		print(b.hash)


scheduler = BackgroundScheduler()
scheduler.add_job(func=main_node_block_miner, trigger="interval", seconds=MINING_INTERVAL_SECONDS)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

def get_return_value(code, data=[]):
	result = {'result_code': code,
				'data': data}
	return json.dumps(result)

@app.route('/miner/queue/number', methods=['GET'])
def get_miner_queue_number():
	return get_return_value(ReturnCode.OK.value, blockchain.miner_queue_number)

@app.route('/newblock', methods=['POST'])
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

@app.route('/addnode', methods=['POST'])
def add_node():
	try:
		port = request.get_json()['url']
		blockchain.add_node(port)
	except:
		return get_return_value(ReturnCode.INVALID_ARGUMENT.value)
	return get_return_value(ReturnCode.OK.value)

@app.route('/nodes', methods=['GET'])
def get_nodes():
	return get_return_value(ReturnCode.OK.value, blockchain.get_friendly_nodes())


@app.route('/transactions/pendings', methods=['GET'])
def get_pending_thxs():
	serialized_transactions = FileSystem.getTransactionsFromMempool()
	dictionary_array = []
	for s in serialized_transactions:
		dictionary_array.append(Deserializer.deserialize(s).to_dictionary())
	return get_return_value(ReturnCode.OK.value, dictionary_array)

@app.route('/chain', methods=['GET'])
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

@app.route('/chain/length', methods=['GET'])
def get_chain_length():
	chain = blockchain.get_full_chain()
	return get_return_value(ReturnCode.OK.value, len(chain))

def get_transactions_by_cargo_id(cargo_id):
	data = []
	chain = blockchain.get_full_chain()
	for block in chain:
		for tx in block.transactions:
			tx_obj = Deserializer.deserialize(tx)
			if tx_obj.cargo_id == cargo_id:
				data.append(tx_obj.to_dictionary())
	if data == []:
		return (ReturnCode.CARGO_ID_NOT_FOUND, [])
	return (ReturnCode.OK, data)

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	tx = None
	try:
		serialized_tx = request.get_json()['serialized']
		tx = Deserializer.deserialize(serialized_tx)
	except:
		try:
			dictionary_tx = request.get_json()['dictionary']
			tx = Transaction.from_dict(dictionary_tx)
		except Exception as m:
			return get_return_value(ReturnCode.INVALID_ARGUMENT.value)

	pool = FileSystem.getTransactionsFromMempool()
	if (Serializer.serialize(tx) in pool):
		return get_return_value(ReturnCode.CARGO_INFORMATION_ALREADY_EXISTS)

	code = tx_validator.validate_transaction(tx)
	if code.value != ReturnCode.OK.value:
		print("ERROR. Transaction wasn't added. " + color_output.prRed(code.name))
		return get_return_value(code.value)
	FileSystem.addTransactionToMempool(Serializer.serialize(tx))
	return get_return_value(ReturnCode.OK.value)


def get_block_by_height(height):
	chain = blockchain.get_full_chain()
	if chain == []:
		return get_return_value(ReturnCode.EMPTY_CHAIN.value)
	if int(height) >= len(chain):
		return get_return_value(ReturnCode.WRONG_CHAIN_HEIGHT_NUMBER.value)
	return get_return_value(ReturnCode.OK.value, chain[height].to_dictionary())

@app.route('/find/', methods=['GET'])
def find():
	param = request.args.get('cargo_id')
	if param is not None:
		data = get_transactions_by_cargo_id(param)
		return get_return_value(data[0].value, data[1])
	param = int(request.args.get('block_by_height'))
	if param is not None:
		return get_block_by_height(param)
	return get_return_value(ReturnCode.INVALID_ARGUMENT.value)

@app.route('/')
def get_hello():
	return render_template('index.html')


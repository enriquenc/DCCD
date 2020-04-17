import time
import json
from flask import Flask
from flask import request
from multiprocessing import Process, Pipe
import blockchain
import block
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

from config import URL, NODE_PORT

node = Flask(__name__)
CORS(node)

BLOCKCHAIN = []
NODES = []

"""служебные функции"""

def to_object(data):
    b = block.Block(data['timestamp'], data['previous_hash'],
                          data['transactions'])
    b.hash = data['hash']
    b.nonce = data['nonce']
    b.merkle_root = data['merkle_root']
    return b

def to_dictionary(blckchain):
    dct = []
    d = blckchain.copy()
    for blck in d:
        dct.append({
            'timestamp' : blck.timestamp,
            'nonce' : blck.nonce,
            'previous_hash' : blck.previous_hash,
            'transactions' : blck.transactions,
            'merkle_root' : blck.merkle_root,
            'hash' : blck.hash,
        })

    return dct

def dictionary_to_list(dct):
    lst = []
    b = None
    for blck in dct:
        b = block.Block(blck['timestamp'], blck['previous_hash'], blck['transactions'])
        b.nonce = blck['nonce']
        b.merkle_root = blck['merkle_root']
        b.hash = blck['hash']
        lst.append(b)
    return lst

def load_chain(blckchn):
    try:
        i = 0
        b = None
        while True:
            with open('blocks/' + '%04d' % i + '.block') as json_file:
                data = json.load(json_file)
            b = to_object(data)
            blckchn.append(b)
            json_file.close()
            i = i + 1
    except:
        pass
    return blckchn

def obj_to_dictionary(blck):

    d = {
        'timestamp' : blck.timestamp,
        'nonce' : blck.nonce,
        'previous_hash' : blck.previous_hash,
        'transactions' : blck.transactions,
        'merkle_root' : blck.merkle_root,
        'hash' : blck.hash,
    }
    return d


"""api функции"""


@node.route('/utxo')
def utxo():
    "[TODO] Return utxo list"
    return

@node.route('/newblock', methods=['POST'])
def new_block():
    global BLOCKCHAIN
    if request.method == 'POST':
        b = request.get_json()
        #d = json.loads(b.decode('utf-8'))
        blck = to_object(b)
        if block_validator.validate(blck):
            BLOCKCHAIN.append(blck)
        "[TODO] Remove transactions from mempool"
        "[TODO] Remove spended utxo and added new"

        with open('blocks/' + '%04d' % int(BLOCKCHAIN.index(blck)) + '.block', 'w') as outfile:
                json.dump(b, outfile)
        return 'Added'

@node.route('/addnode',methods=['POST'])
def add_node():
    if request.method == 'POST':
        port = request.get_json()['port']
        f = open('nodes.config', 'a+')
        f.write(port + '\n')
        f.close()
    return 'True'

@node.route('/transactions/new', methods=['POST'])
def submit_tx():
    "[TODO] send to all nodes"
    if request.method == 'POST':
        pending_pool.pending_pool(request.get_json()['serialized'])
    return 'okay'

@node.route('/transactions/pendings')
def pending_thxs():
    f = open('mempool', 'r')
    txs = f.readlines()
    t = []
    for i in txs:
        t.append(i[:-1])
    f.close()
    return json.dumps(t)


@node.route('/chain')
def chain():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    BLOCKCHAIN = load_chain(BLOCKCHAIN)
    return json.dumps(to_dictionary(BLOCKCHAIN))

@node.route('/chain/length')
def chain_length():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    load_chain(BLOCKCHAIN)
    length = {'length' : len(BLOCKCHAIN)}
    length = json.dumps(length)
    return (length)

@node.route('/nodes')
def nodes():
    f = open('nodes.config', 'r')
    nodes = f.readlines()
    f.close()
    for i in range(len(nodes)):
        nodes[i] = nodes[i][:-1]
    return json.dumps(nodes)


@node.route('/block/', methods=['GET'])
def get_n_block():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    BLOCKCHAIN = load_chain(BLOCKCHAIN)
    height = int(request.args.get('height'))

    print(height)
    print(len(BLOCKCHAIN))
    if height >= len(BLOCKCHAIN):
        d = {}
        return json.dumps(d)
    else:
        json_block = json.dumps(obj_to_dictionary(BLOCKCHAIN[height]))
        return json_block

@node.route('/block/last')
def get_last_block():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    BLOCKCHAIN = load_chain(BLOCKCHAIN)
    return json.dumps(obj_to_dictionary(BLOCKCHAIN[-1]))

@node.route('/balance')
def get_balance():
    global BLOCKCHAIN
    BLOCKCHAIN = []
    BLOCKCHAIN = load_chain(BLOCKCHAIN)
    addr = str(request.args.get('addr'))
    balance = 0
    for b in BLOCKCHAIN :
            if BLOCKCHAIN.index(b) == 0:
                tx = pending_pool.make_obj(b.transactions)
                if tx.sender == addr:
                    balance = balance - tx.amount
                elif tx.recipient == addr:
                    balance = balance + tx.amount
            else:
                for t in b.transactions:
                    #print(t)
                    tx = pending_pool.make_obj(t)
                    if tx.sender == addr:
                        balance = balance - int(tx.amount)
                    elif tx.recipient == addr:
                        balance = balance + int(tx.amount)
    return json.dumps(balance)

@node.route('/front/transtaction/new', methods=['POST', 'OPTIONS'])
def get_front_new_transaction():
    data = request.get_json()
    cargo_id = data['cargo_id']
    private_key = data['private_key']
    trn = transaction.Transaction(sender, cargo_id)
    trn.sign(self.private_key)
    tx_validator.validation(trn)
    print(serializer.Serializer.serialize(trn))
    return 'okay'

@node.route('/front/find/cargoid', methods=['GET'])
def get_info_by_cargo_id():
    cargo_id = request.args.get('cargo_id')
    print(cargo_id)
    return pending_thxs()


@node.route('/')
def get_hello():
    return json.dumps("HELLO DCCD")


if __name__ == '__main__':
    p2 = Process(target = node.run(port = NODE_PORT))
    p2.start()

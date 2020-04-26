from flask import Flask
from flask import request
from flask_cors import CORS
import json
from multiprocessing import Process, Pipe

node = Flask(__name__)
CORS(node)

@node.route('/reader/data', methods=['GET'])
def get_reader_data():
	tx = {'cargo_id' : "1231231231",
		'reader_number' : "1"}
	length = json.dumps(tx)
	return (length)

if __name__ == '__main__':
	p2 = Process(target = node.run(port = 5000))
	p2.start()


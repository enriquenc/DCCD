import requests


def get_miner_queue_number_list(url, nodes):
	queue = []
	for node in nodes:
		data = requests.get(url + node + '/miner/queue/number').json()
		if data == 'result_code' != 0:
			continue
		queue.append(data['data'])
	return queue

import requests


def get_miner_queue_number_list(url, nodes):
	queue = []
	for node in nodes:
		node = requests.get(url + node + '/miner/queue/number').content.decode('utf-8')
		if node == 'null':
			continue
		queue.append(node)
	return queue

import requests


def get_miner_queue_number_list(friendly_nodes):
	queue = []
	for url in friendly_nodes:
		try:
			data = requests.get(url + '/miner/queue/number').json()
		except:
			continue
		if data == 'result_code' != 0:
			continue
		queue.append(data['data'])
	return queue

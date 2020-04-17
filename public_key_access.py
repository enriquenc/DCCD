
def get_creators_public_keys():
	f = open("creators_public_keys", 'r')
	keys = f.read().split('\n')
	return keys

def get_validators_public_keys():
	f = open("validators_public_keys", 'r')
	keys = f.read().split('\n')
	return keys


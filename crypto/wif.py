import hashlib
import base58
import binascii


def privToWif(private_key):
	versioned_key = "80" + private_key
	priv_hash_1 = hashlib.sha256(binascii.unhexlify(versioned_key)).hexdigest()
	priv_hash_2 = hashlib.sha256(binascii.unhexlify(priv_hash_1)).hexdigest()
	binary_data = versioned_key + str(priv_hash_2)[:8]
	wif = base58.b58encode(binascii.unhexlify(binary_data))
	return wif.decode('utf-8')

def wifToPriv(wif):
	binary_data = base58.b58decode(wif)
	hex_data = binascii.hexlify(binary_data)
	check_sum = hex_data[-8:]
	versioned_key = hex_data[0:-8]
	priv_hash_1 = hashlib.sha256(binascii.unhexlify(versioned_key)).hexdigest()
	priv_hash_2 = hashlib.sha256(binascii.unhexlify(priv_hash_1)).hexdigest()
	check_sum_of_hash = str(priv_hash_2)[0:8].encode('utf-8')
	assert check_sum == check_sum_of_hash , "Houston we've got a problem with WIF key"
	private_key = versioned_key[2:]
	return private_key.decode('utf-8')

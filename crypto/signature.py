
import codecs
import hashlib
import ecdsa

def privToPub(private_key):
	priv_key_bytes = codecs.decode(private_key, 'hex')
	key = ecdsa.SigningKey.from_string(priv_key_bytes, curve=ecdsa.SECP256k1).verifying_key
	key_bytes = key.to_string()
	key_hex = codecs.encode(key_bytes, 'hex')
	btc_byte = b'04'
	public_key = btc_byte + key_hex
	return public_key.decode('utf-8')

def digital_signature(private_key, message):
	private_key_bytes = codecs.decode(private_key, 'hex')
	sk = ecdsa.SigningKey.from_string(private_key_bytes, curve = ecdsa.SECP256k1, hashfunc=hashlib.sha256)
	signed_msg = sk.sign(message.encode('utf-8'))
	return (signed_msg.hex(), privToPub(private_key))


def sign_verify(signed_message, public_key, message):
	vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key[2:]), curve=ecdsa.SECP256k1, hashfunc=hashlib.sha256)
	try:
		vk.verify(bytes.fromhex(signed_message), message.encode('utf-8'))
	except:
		return False
	return True
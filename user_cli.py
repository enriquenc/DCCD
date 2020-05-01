import wallet
import transaction
import cmd, sys
import tx_validator
import serializer
import pending_pool
import requests
from config import URL, NODE_PORT
import json
import time

class UserCli(cmd.Cmd):
	intro = "Welcome to the DCD user-cli shell. Type help or ? to list commands. \n"
	prompt = '(user-cli) '
	file = None
	private_key = None

	def do_new(self, arg):
		kg = wallet.KeyGenerator()
		self.private_key = kg.generate_key()
		self.print_it(self.private_key)

	def do_import(self, arg):
		wif = None
		try:
			with open(arg, 'r') as f:
				wif = f.readline()
		except:
			print(arg + ": invalid file or directory")
			return
		try:
			self.private_key = wallet.wifToPriv(wif)
		except Exception as e:
			print(str(e))
			return
		self.print_it(self.private_key)

	def do_privtowif(self, arg):
		self.file = open('private_key.wif', "w+")
		self.file.write(str(wallet.privToWif(arg)))
		self.file.close()
		print('Private key saved to private_key.wif file')

	def do_exit(self, arg):
		print('Thank you for using wallet-cli :)')
		return True

	def do_send(self, arg):
		trn = transaction.Transaction(arg, str(time.time()))
		trn.sign(self.private_key)
		print(serializer.Serializer.serialize(trn))

	def do_broadcast(self, arg):
		arg = arg.replace(' ', '')
		if arg == '':
			print('broadcast <serialized transaction>')
			return

		# if tx_validator.validate_transaction(serializer.Deserializer.deserialize(arg)) == False:
		# 	print('Invalid transaction.')
		# 	return
		tx = {'serialized' : arg}
		response = requests.post(URL + NODE_PORT + '/transactions/new', json = tx)
		print(response.content)
		print(serializer.Deserializer.deserialize(arg).to_dictionary())
		if response.status_code != 200 or json.loads(response.content.decode('utf-8'))['result_code'] != 0:
			print('Error in sending transaction.')
			return
		print('Transaction sent.')

	def print_it(self, priv):
		print("Private key: " + priv)


if __name__ == '__main__':
	UserCli().cmdloop()
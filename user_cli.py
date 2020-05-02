import wallet
from transaction import Transaction
import cmd, sys
import tx_validator
from serializer import Deserializer, Serializer
import requests
from config import URL, NODE_PORT
import json
import time
from return_code import ReturnCode
class UserCli(cmd.Cmd):
	intro = "Welcome to the DCD user-cli shell. Type help or ? to list commands. \n"
	prompt = '(user-cli) '
	file = None
	private_key = None
	last_serialized = None

	def do_new(self, arg):
		kg = wallet.KeyGenerator()
		self.private_key = kg.generate_key()
		print("Private key: " + self.private_key)

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
		print("Private key: " + self.private_key)

	def do_privtowif(self, arg):
		fname = 'private_key.wif'
		with open(fname, "w+"):
			self.file.write(str(wallet.privToWif(arg)))
		print('Private key saved to ' + fname + ' file')

	def do_exit(self, arg):
		print('Thank you for using wallet-cli :)')
		return True

	def do_send(self, arg):
		trn = Transaction(arg, str(time.time()))
		trn.sign(self.private_key)
		self.last_serialized = Serializer.serialize(trn)
		print(self.last_serialized)

	def do_broadcast(self, arg):
		arg = arg.replace(' ', '')
		if arg == '':
			if self.last_serialized is None:
				print('broadcast <serialized transaction>')
				return
			print('Took last serialized transaction')
			arg = self.last_serialized

		if tx_validator.validate_transaction(Deserializer.deserialize(arg)) != ReturnCode.OK:
			print('Invalid transaction.')
			return
		tx = {'serialized' : arg}
		response = requests.post(URL + NODE_PORT + '/transactions/new', json = tx)
		if response.status_code != 200 or json.loads(response.content.decode('utf-8'))['result_code'] != 0:
			print('Error in sending transaction.')
			return
		print('Transaction sent.')

if __name__ == '__main__':
	UserCli().cmdloop()
import wallet
import transaction
import cmd, sys
from turtle import *
import tx_validator
import serializer
import test
import pending_pool
import requests
from config import URL, NODE_PORT
import json
import initializer as system
from time import asctime, gmtime

class WalletCli(cmd.Cmd):
    intro = "Welcome to the tmaslyanpitcoin's wallet-cli shell. Type help or ? to list commands. \n"
    prompt = '(wallet-cli) '
    file = None
    private_key = None

    def do_new(self, arg):
        kg = wallet.KeyGenerator()
        self.private_key = kg.generate_key()
        addr = wallet.pubToAddress(wallet.privToPub(self.private_key))
        self.print_it(self.private_key, addr)

    def do_import(self, arg):
        try:
            self.file = open(arg, "r")
        except:
            print(arg + ": invalid file or directory")
            return
        wif = self.file.read()
        try:
            self.private_key = wallet.wifToPriv(wif)
        except Exception as e:
            print(str(e))
            return
        addr = wallet.pubToAddress(wallet.privToPub(self.private_key))
        self.print_it(self.private_key, addr)
        self.file.close()

    def do_privtowif(self, arg):
        self.file = open('private_key.wif', "w+")
        self.file.write(str(wallet.privToWif(arg)))
        self.file.close()
        print('Private key saved to private_key.wif file')

    def do_exit(self, arg):
        print('Thank you for using wallet-cli :)')
        bye()
        return True

    def do_send(self, arg):
        trn = transaction.Transaction(arg, asctime(gmtime()))
        trn.sign(self.private_key)
        #tx_validator.validate_transaction(trn)

        print(serializer.Serializer.serialize(trn))

    def do_broadcast(self, arg):
        arg = arg.replace(' ', '')
        if arg == '':
            print('broadcast <serialized transaction>')
            return

        if tx_validator.validate_transaction(pending_pool.make_obj(arg)) == False:
            return
        print('Transaction sent.')
        tx = {'serialized' : arg}
        requests.post(URL + NODE_PORT + '/transactions/new', json = tx)


    def do_balance(self, arg):
        try:
            balance = requests.get(URL + NODE_PORT + '/balance?addr=' + arg).content
        except:
            print('Please, run RPC server.')
            return
        print(json.loads(balance))


    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def print_it(self, priv, pub):
        print("Private key:", end = ' ')
        print(priv)
        self.file = open('public_address', 'w+')
        self.file.write(pub)
        print("Public address saved in public_address file.")
        self.file.close()



if __name__ == '__main__':
    WalletCli().cmdloop()
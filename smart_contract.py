import hashlib
import wallet

class SmartContract:
    def __init__(self, sender, data):
        self.sender = sender
        self.data = data
        self.timestamp = None
        self.public_key = None

    def calculate_hash(self):
        concatenation = self.sender + self.cargo_id + self.timestamp
        trn_hash = hashlib.sha256(concatenation.encode('utf-8')).hexdigest()
        return trn_hash

    def sign(self, private_key):
        try:
            sp = wallet.digital_signature(private_key, self.calculate_hash())
            self.signed_hash = sp[0]
            self.public_key = sp[1]
        except:
            raise Exception('Invalid transaction.')

class BaseSmartContract(SmartContract):
    def __init__(self, recipient):
        super(BaseSmartContract, self).__init__(sender, 50)

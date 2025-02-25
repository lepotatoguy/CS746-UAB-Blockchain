from merkle_tree import *
from utils import *
from utxo import *


class Transaction:
    def __init__(
        self, user_name=None, recipient=None, amount=0, coinbase=False
    ) -> None:
        self.sender = user_name
        if not coinbase:
            self.sender_address = publickey2address(load_public_key(self.sender))
        self.sender_password = None
        self.recipient = recipient
        self.recipient_address = publickey2address(load_public_key(self.recipient))
        self.amount = int(amount)
        self.change = None
        self.coinbase = coinbase
        self.reward = 100
        if coinbase:
            self.utxo = UTXO(True)
        else:
            self.utxo = UTXO()

    # transaction format
    def info2dict(self):
        self.content = {
            "timestamp": get_time(),
            "from": self.sender_address,
            "to": self.recipient_address,
            "amount": self.amount,
        }
        self.copyInfo(self.content)
        return self.content

    # sign data with signature
    def sign(self, content):
        if not self.coinbase:
            self.sender_password = input("Enter your password: ")
            sender_private_key = load_private_key(self.sender, self.sender_password)
            signature = sign_message(content, sender_private_key)
            self.content["signature"] = signature.hex()

    # create coinbaseTx
    def calculate_coinbase(self):
        self.utxo.create_utxo(self.sender, None, self.recipient, self.reward)

    # generate utxo
    def calculate_utxo(self):
        if not self.coinbase:
            utxo_files = self.utxo.load_utxo_set(self.sender)
            utxo_dict = {}
            self.change = 0
            amount = self.amount
            for key, value in utxo_files.items():
                if amount != 0:
                    # if value of utxo > amount, create spent value utxo and change utxo
                    if value > amount:
                        self.change = value - amount
                        utxo_dict[key] = amount
                        self.utxo.create_utxo(
                            self.sender, self.sender_password, self.recipient, amount
                        )
                        self.utxo.create_utxo(
                            self.sender, self.sender_password, self.sender, self.change
                        )
                        self.utxo.remove_utxo(UTXO_DIR, utxo_dict)
                        amount = 0
                    # if value of utxo < amout, move from utxo to pending dir
                    # and calculate change to calculate it again
                    elif value < amount:
                        amount = amount - value
                        utxo_dict[key] = value
                        self.utxo.rename_utxo(UTXO_DIR, PENDING_DIR, utxo_dict)
                    # if they are same, move from utxo to pending dir and end calculation
                    elif value == amount:
                        utxo_dict[key] = value
                        amount = 0
                        self.change = 0
                        self.utxo.rename_utxo(UTXO_DIR, PENDING_DIR, utxo_dict)
                else:
                    break
            return utxo_dict

    # create pending transactions
    def create_pending_tx(self):
        if not self.coinbase:
            utxo_dict = self.calculate_utxo()
            return utxo_dict

    def process(self):
        # check validation
        if not self.coinbase:
            # coinbase has no validation
            valid = Validation(
                self.sender, self.recipient, self.recipient_address, self.amount
            )
            valid.is_valid_amount()
            valid.is_valid_user()
            tx_content = self.info2dict()
            self.sign(tx_content)
            self.create_pending_tx()
        else:
            # create coinbaseTX
            self.calculate_coinbase()


class Validation:
    def __init__(self, sender, recipient, recipient_address, amount) -> None:
        self.sender = sender
        self.recipient = recipient
        self.recipient_address = recipient_address
        self.amount = int(amount)

    # check if it's sufficient to make transactions
    def is_valid_amount(self):
        sender_balance = UTXO().check_balance(self.sender)
        if sender_balance < self.amount:
            print("\nInsufficient Balance")
            exit()
        return True

    # check if it's a valid user
    def is_valid_user(self):
        loaded_address = publickey2address(load_public_key(self.recipient))
        if self.recipient_address == loaded_address:
            return True
        else:
            print("\nInvalid User")
            exit()

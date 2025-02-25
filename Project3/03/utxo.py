from merkle_tree import *
from utils import *


class UTXO:
    def __init__(self, coinbase=False) -> None:
        self.coinbase = coinbase

    # read utxo to check balance
    def load_utxo_set(self, user_name):
        public_key_address = publickey2address(load_public_key(user_name))
        utxo_files = scan_files(UTXO_DIR)

        balances = {}
        for utxo_file in utxo_files:
            utxo_file_path = join(UTXO_DIR, utxo_file)
            with open(utxo_file_path, "r") as f:
                utxo = load(f)
                utxo_address = utxo["to"]
                if public_key_address == utxo_address:
                    balances[utxo_file] = int(utxo["amount"])
        return balances

    # get total balance
    def check_balance(self, user_name):
        utxo_files = self.load_utxo_set(user_name)
        if len(utxo_files) != 0:
            balances = [balance for balance in utxo_files.values()]
            total_balance = sum(balances)
        else:
            total_balance = 0
        return total_balance

    # create utxo for transactions/coinbaseTx
    def create_utxo(
        self, user_name=None, user_password=None, recipient=None, change=None
    ):
        if self.coinbase:
            sender_address = "Miner"
            recipient_address = publickey2address(load_public_key(recipient))
            reward = 100
            change = reward
            sender_private_key = None  # When coinbase is true, this is none
        else:
            sender_private_key = load_private_key(user_name, user_password)
            sender_address = publickey2address(load_public_key(user_name))
            recipient_address = publickey2address(load_public_key(recipient))

        content = {
            "timestamp": get_time(),
            "from": sender_address,
            "to": recipient_address,
            "amount": change,
        }

        # hash file name
        file_name = merkle_tree_hash_root(content)

        # check if it's coinbaseTx
        if self.coinbase:
            signature = "Miners for Justice"
            content["signature"] = signature
            path = join(TRANSACTION_DIR, f"{file_name}.json")
        else:
            signature = sign_message(content, sender_private_key)
            content["signature"] = signature.hex()
            path = join(PENDING_DIR, f"{file_name}.json")
        # create utxo
        create_json_file(path, content)

    # move utxo from from_path to to_path
    def rename_utxo(self, from_, to_, dict):
        for key in dict.keys():
            from_path = join(from_, key)
            to_path = join(to_, key)
            if exists(from_path):
                rename(from_path, to_path)

    # remove utxo
    def remove_utxo(self, path, dict):
        for key in dict.keys():
            file_path = join(path, key)
            if exists(file_path):
                remove(join(path, key))

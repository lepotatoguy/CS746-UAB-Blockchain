import json
import hashlib
import time
import os
import glob
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

TRANSACTION_DIR = 'pending/'
PROCESSED_DIR = 'processed/'
BLOCK_DIR = 'blocks/'
UTXO_FILE = 'utxo/utxo.json'
JSON_EXT = ".json"

class Block:
    def __init__(self):
        self.utxo_file = UTXO_FILE
        self.transaction_dir = TRANSACTION_DIR
        self.processed_dir = PROCESSED_DIR
        self.block_dir = BLOCK_DIR

    @staticmethod
    def hashing(data):
        return hashlib.sha256(data.encode()).hexdigest()

    def get_previous_block_hash(self):
        block_files = sorted(glob.glob(self.block_dir + "*" + JSON_EXT))
        if block_files:
            last_block_file = block_files[-1]
            with open(last_block_file, 'r') as f:
                last_block = json.load(f)
                return last_block["header"]["hash"]
        return "NA"

    def get_balance(self, address):
        utxo = self.load_utxo()
        if address in utxo:
            return sum([entry["amount"] for entry in utxo[address]])
        return 0

    def add_transactions(self):
        valid_transactions = []
        for trans_file in glob.glob(self.transaction_dir + "*" + JSON_EXT):
            with open(trans_file, 'r') as f:
                transaction = json.load(f)
                # Validate the transaction
                if self.validate_transaction(transaction):
                    valid_transactions.append({
                        "hash": os.path.basename(trans_file).replace(JSON_EXT, ""),
                        "content": transaction
                    })
                    os.rename(trans_file, self.processed_dir + os.path.basename(trans_file))
                    print(f"{trans_file} is moved into the processed directory!")
        return valid_transactions

    def validate_transaction(self, transaction):
        # Check if sender has enough balance
        if self.get_balance(transaction.get('from')) < transaction.get('amount'):
            print(f"Transaction rejected! Insufficient funds for {transaction.get('from')}.")
            return False

        # Validate signature
        sender_public_key = RSA.import_key(transaction['from_public_key'])
        # sender_public_key = transaction['from_public_key']
        h = SHA256.new(json.dumps({key: transaction[key] for key in transaction if key != 'signature'}, separators=(',', ':')).encode())
        signature = bytes.fromhex(transaction['signature'])
        try:
            pkcs1_15.new(sender_public_key).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False

    def create_dir(self):
        if not os.path.exists(self.transaction_dir):
            os.makedirs(self.transaction_dir)
        if not os.path.exists(self.block_dir):
            os.makedirs(self.block_dir)
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

    def load_utxo(self):
        if os.path.exists(self.utxo_file):
            with open(self.utxo_file, 'r') as f:
                return json.load(f)
        return {}

    def save_utxo(self, utxo):
        with open(self.utxo_file, 'w') as f:
            json.dump(utxo, f)

    @staticmethod
    def sanitize_public_key(raw_key):
        """Sanitize the public key for easy copy-pasting."""
        # Removing the header/footer and newlines
        return raw_key.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "")

    def update_utxo(self, transactions):
        utxo = self.load_utxo()
        for transaction in transactions:
            content = transaction['content']
            from_acc = content['from']
            to_acc = content['to']
            amount = content['amount']
            from_public_key = content['from_public_key']
            to_public_key = content['to_public_key']        
            
            # Deduct from the sender
            if from_acc in utxo:
                sender_utxos = utxo[from_acc]
                amt_to_deduct = amount
                # Deduct from each UTXO till the amount is covered
                while amt_to_deduct > 0 and sender_utxos:
                    current_utxo = sender_utxos.pop(0)  # Consume the oldest UTXO first
                    if current_utxo['amount'] <= amt_to_deduct:
                        amt_to_deduct -= current_utxo['amount']
                    else:
                        change = current_utxo['amount'] - amt_to_deduct
                        sender_sanitized_key = self.sanitize_public_key(from_public_key)
                        sender_utxos.append({'tx_id': transaction['hash'], 'amount': change, 'public_key': sender_sanitized_key})
                        print()
                        print('change: ', change)
                        print()
                        amt_to_deduct = 0
                utxo[from_acc] = sender_utxos

            # Add to the receiver
            receiver_sanitized_key = self.sanitize_public_key(to_public_key)
            if to_acc in utxo:
                utxo[to_acc].append({'tx_id': transaction['hash'], 'amount': amount, 'public_key': to_public_key})
            else:
                utxo[to_acc] = [{'tx_id': transaction['hash'], 'amount': amount, 'public_key': to_public_key}]
            
        self.save_utxo(utxo)

    def add_transactions_into_JSON(self, transactions, timestamp, previous_block_hash):
        """
        Format transactions into the expected block structure.
        """
        header = {
            "prev_hash": previous_block_hash,
            "timestamp": timestamp,
            "merkle_root": "PLACEHOLDER"  # We can calculate this later if needed
        }
        
        block = {
            "header": header,
            "transactions": transactions
        }
        
        # Update the header hash
        header["hash"] = self.hashing(json.dumps(header))
        
        return header, block
    
    def create_block(self, header, block):
        """
        Serialize the block into JSON and save it to the blocks directory.
        """
        block_name = header["hash"]
        with open(self.block_dir + f"{block_name}.json", 'w') as f:
            json.dump(block, f)
        print(f"Block saved with name {block_name}.json")
        
        # Update UTXOs
        self.update_utxo([trans_data for trans_data in block["transactions"]])

    def process(self):
        self.create_dir()
        transactions = self.add_transactions()
        timestamp = int(time.time())
        previous_block_hash = self.get_previous_block_hash()
        header, block = self.add_transactions_into_JSON(transactions, timestamp, previous_block_hash)
        self.create_block(header, block)

if __name__ == '__main__':
    block = Block()
    while True:
        option = input(
            "\n---------------------------------------------\n"
            "1. Create block\n"
            "2. Exit\n"
            "---------------------------------------------\n"
            "Enter your option: ")

        if option == '1':
            block.process()
        elif option == '2':
            break
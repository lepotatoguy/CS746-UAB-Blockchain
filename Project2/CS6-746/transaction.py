import json
import time
import hashlib
import os
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

PENDING_TRANSACTIONS_DIR = 'pending/'
UTXO_FILE = 'utxo/utxo.json'
KEYS_DIR = 'wallet_keys'
PUBLIC_DIR = KEYS_DIR + '/public_keys'
class Transaction:
    def __init__(self):
        self.pending_transactions_dir = PENDING_TRANSACTIONS_DIR
        self.utxo_file = UTXO_FILE

        if not os.path.exists(self.pending_transactions_dir):
            os.makedirs(self.pending_transactions_dir)

    def load_utxo(self):
        if os.path.exists(self.utxo_file):
            with open(self.utxo_file, 'r') as f:
                return json.load(f)
        return {}

    def is_valid_user(self, address):
        utxo = self.load_utxo()
        return address in utxo

    def get_balance(self, address):
        utxo = self.load_utxo()
        return sum([entry["amount"] for entry in utxo.get(address, [])])

    def get_private_key(self, user):
        """Retrieve the private key of the user."""
        try:
            key_path = os.path.join(KEYS_DIR, f"{user}_private.pem")
            with open(key_path, 'r') as f:
                return RSA.import_key(f.read())
        except FileNotFoundError:
            return None

    @staticmethod
    def sanitize_public_key(raw_key):
        """Sanitize the public key for easy copy-pasting."""
        # Removing the header/footer and newlines
        return raw_key.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "")

    def create_transaction(self):
        sender_name = input("\nEnter the sender's name (e.g., Alice): ")

        if not self.is_valid_user(sender_name):
            print(f"{sender_name} does not have an account.")
            return

        receiver_name = input("Enter the receiver's name (e.g., Bob): ")
        if not self.is_valid_user(receiver_name):
            print(f"{receiver_name} does not have an account.")
            return

        receiver_public_key_str = input("Enter the receiver's public key: ")  
        with open(PUBLIC_DIR +f"/{receiver_name}_public.txt", 'r') as f:       
            receiver_public_key = f.read()                        
        try:
            receiver_public_key_str == receiver_public_key            
        except ValueError:
            print("Invalid public key provided.")
            return

        try:
            amount = int(input("Enter the amount: "))
        except ValueError:
            print("Invalid amount entered. Please enter a numeric value.")
            return

        if self.get_balance(sender_name) < amount:
            print(f"Insufficient funds for {sender_name}.")
            return

        timestamp = int(time.time())        
        from_private_key = self.get_private_key(sender_name).publickey().export_key(format='PEM').decode()
        sanitized_key = self.sanitize_public_key(from_private_key)
        transaction = {
            'from': sender_name,
            'to': receiver_name,
            'amount': amount,
            'timestamp': timestamp,
            "from_public_key": from_private_key,
            'to_public_key': receiver_public_key
        }

        # Use the sender's private key to sign the transaction.
        sender_private_key = self.get_private_key(sender_name)
        if not sender_private_key:
            print("Unable to retrieve sender's private key. Transaction failed.")
            return

        h = SHA256.new(json.dumps({key: transaction[key] for key in transaction}, separators=(',', ':')).encode())
        signature = pkcs1_15.new(sender_private_key).sign(h)
        transaction['signature'] = signature.hex()

        transaction_name = self.hashing(str(transaction))
        with open(self.pending_transactions_dir + f"{transaction_name}.json", 'w') as f:
            json.dump(transaction, f)
        print(f"Transaction saved with name {transaction_name}.json")

    @staticmethod
    def hashing(data):
        return hashlib.sha256(data.encode()).hexdigest()

    def main_menu(self):
        while True:
            option = input(
                "\n---------------------------------------------\n"
                "1. Create transaction\n"
                "2. Exit\n"
                "---------------------------------------------\n"
                "Enter your option: ")

            if option == '1':
                self.create_transaction()
            elif option == '2':
                break

    def save_utxo(self, utxo):
        """Save the UTXO to the file."""
        with open(self.utxo_file, 'w') as f:
            json.dump(utxo, f)

if __name__ == '__main__':
    transaction = Transaction()
    transaction.main_menu()

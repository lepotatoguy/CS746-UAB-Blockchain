import os
import json
from Crypto.PublicKey import RSA
from transaction import Transaction
from block import Block

UTXO_DIR = 'utxo'
UTXO_FILE = os.path.join(UTXO_DIR, 'utxo.json')
KEYS_DIR = 'wallet_keys'
PUBLIC_DIR = KEYS_DIR + '/public_keys'

class Wallet:
    def __init__(self):
        self.ensure_dir_exists(KEYS_DIR)
        self.ensure_dir_exists(UTXO_DIR)
        self.ensure_dir_exists(PUBLIC_DIR)
        
    def create_transaction(self):
        transaction = Transaction()
        transaction.create_transaction()

    @staticmethod
    def ensure_dir_exists(dir_name):
        """Ensure the specified directory exists. If not, create it."""
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def create_wallet(self):
        """Create a new wallet for the owner."""
        owner_name = input("\nEnter your name: ")
        provided_public_key = input("\nIf you already have a wallet, provide the sanitized public key, else press enter: ")

        if self.owner_exists(owner_name, provided_public_key):            
            print("\nWallet for this owner already exists or public key does not match!")                
            return

        private_key = RSA.generate(2048)        
        wallet_path = self.get_wallet_path(owner_name)
        with open(wallet_path, 'wb') as priv_file:
            priv_file.write(private_key.export_key())

        raw_public_key = private_key.publickey().export_key().decode()
        sanitized_public_key = self.sanitize_public_key(raw_public_key)
        print(f"\nPrivate key saved as {owner_name}_private.pem in the {KEYS_DIR} directory.")
        print(f"\nYour sanitized public key: {sanitized_public_key}")

        # Add input for initial balance
        initial_balance = float(input("\nEnter initial balance for the wallet: "))
        self.add_balance_to_utxo(owner_name, sanitized_public_key, initial_balance)    
                
        # Save public key to a separate file
        with open(PUBLIC_DIR +f"/{owner_name}_public.txt", 'w') as f:                                    
            f.write(sanitized_public_key)
        
    @staticmethod
    def sanitize_public_key(raw_key):
        """Sanitize the public key for easy copy-pasting."""
        # Removing the header/footer and newlines
        return raw_key.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "")

    def get_wallet_path(self, owner_name):
        """Return the path of the wallet file for the specified owner."""
        return os.path.join(KEYS_DIR, f"{owner_name}_private.pem")

    def owner_exists(self, owner_name, provided_public_key=None):
        """Check if the owner already has a wallet and matches the public key (if provided)."""
        wallet_path = self.get_wallet_path(owner_name)
        if not os.path.exists(wallet_path):
            return False
        if provided_public_key:
            with open(wallet_path, 'rb') as priv_file:
                private_key = RSA.import_key(priv_file.read())
                derived_public_key = private_key.publickey().export_key().decode()
                sanitized_derived_public_key = self.sanitize_public_key(derived_public_key)                   
                return sanitized_derived_public_key == provided_public_key                
        return True

    def add_balance_to_utxo(self, owner_name, public_key, amount):
        """Add the given balance to the UTXO for the specified owner and public key."""
        utxo = self.load_utxo()
        
        # If owner doesn't exist in the UTXO, create an entry
        if owner_name not in utxo:
            utxo[owner_name] = []

        # Append the new balance
        utxo[owner_name].append({
            "public_key": public_key,
            "amount": amount
        })
        
        tx = Transaction()
        tx.save_utxo(utxo)
        

    def check_balance(self):
        """Check the balance of the owner."""
        owner_name = input("\nEnter the owner's name: ")
        owner_public_key = self.sanitize_public_key(input("\nEnter the owner's public key: "))

        if not self.owner_exists(owner_name, owner_public_key):            
            print("\nNo wallet found for this owner or public key does not match!")
            return

        utxo = self.load_utxo()        
        
        # Check if the owner exists in the UTXO
        if owner_name not in utxo:
            print(f"\nThe owner {owner_name} has no transactions yet!")
            return

        # Check if the provided public key matches any of the public keys associated with the owner in the UTXO
        matching_utxo_entries = [entry for entry in utxo[owner_name] if entry['public_key'] == owner_public_key]

        
        balance = sum([entry["amount"] for entry in matching_utxo_entries])
        
        if balance == 0 and not matching_utxo_entries:
            print(f"\nPublic key does not match any transactions for the owner {owner_name}!")
            return
        else:
            print(f"\nBalance for {owner_name}: {balance}")

    def check_balance_of_address(self):
        """Check the balance of a given public address."""
        public_address = input("\nEnter the public address: ")
        utxo = self.load_utxo()

        # Sum amounts in all UTXOs for the address
        balance = sum([entry["amount"] for owner in utxo for entry in utxo[owner] if entry['public_key'] == public_address])

        if balance == 0:
            print(f"\nNo transactions found for the provided public address!")
            print("balance: ", balance)
        else:
            print(f"\nBalance for the provided public address: {balance}")

    @staticmethod
    def load_utxo():
        """Load Unspent Transaction Outputs (UTXO)."""
        if os.path.exists(UTXO_FILE):
            with open(UTXO_FILE, 'r') as f:
                return json.load(f)
        return {}

    def list_public_addresses(self):
        """List all public addresses."""
        utxo = self.load_utxo()

        if not utxo:
            print("\nNo public addresses found!")
            return

        all_addresses = set()
        for owner in utxo:
            for entry in utxo[owner]:
                all_addresses.add(entry['public_key'])
        
        if not all_addresses:
            print("\nNo public addresses found!")
        else:
            print("\nPublic Addresses:")
            for address in all_addresses:
                print(address)

    def create_block(self):
        block = Block()
        block.process()

    def main_menu(self):
        """Display the main menu."""
        while True:
            print(
                "\n---------------------------------------------\n"
                "1. Create a wallet\n"
                "2. Check your balance\n"
                "3. Check another's balance\n"                
                "4. Create a transaction\n"
                "5. Create a block\n"
                "6. Exit\n"
                "---------------------------------------------\n"
            )

            option = input("Enter your option: ")

            if option == '1':
                self.create_wallet()
            elif option == '2':
                self.check_balance()
            elif option == '3':
                self.check_balance_of_address()
            elif option == '4':
                # self.list_public_addresses()
                self.create_transaction()
            elif option == '5':
                self.create_block()
            elif option == '6':
                break
            # elif option == '7':
            else:
                print("\nInvalid option! Try again.")

if __name__ == '__main__':
    wallet = Wallet()
    wallet.main_menu()

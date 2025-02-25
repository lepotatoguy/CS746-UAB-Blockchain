from block import Block
from node import *
from transaction import Transaction
from utils import *
from utxo import UTXO


class Wallet:
    def __init__(self, user_name, user_password) -> None:
        self.user_name = user_name
        self.user_password = user_password

    # create wallet/private key/public key
    def create_new_key(self, user_name, user_password):
        # create private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # create private pem
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                user_password.encode("utf-8")
            ),
        )

        private_key_path = join(PRIVATE_KEY_DIR, f"{user_name}.pem")
        # create private pem file
        create_bytes_file(private_key_path, pem)

        # create public key
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1
        )
        public_key_path = join(PUBLIC_KEY_DIR, user_name)
        # create public key file
        create_bytes_file(public_key_path, public_key_bytes)

        # create address file for test
        create_address(user_name)
        return private_key

    # check balance by calculating utxo
    def check_balance(self):
        file_list = scan_files(PUBLIC_KEY_DIR)
        chosen_user_name = list_files(file_list)
        balance = UTXO().check_balance(chosen_user_name)
        print(f"\n{chosen_user_name}'s balance is {int(balance):,} coins.")


def main():
    create_dir()
    print("Sign-in")
    user_name = input("Enter your name: ")
    user_exists = exists(join(PRIVATE_KEY_DIR, f"{user_name}.pem"))
    user_password = input("Enter your password: ")
    wallet = Wallet(user_name, user_password)
    if user_exists:
        wallet.private_key = load_private_key(user_name, user_password)
        create_address(user_name)
    else:
        wallet.private_key = wallet.create_new_key(user_name, user_password)

    while True:
        print(f"\n{' Menu ':=^40}")
        print(
            "0. Delete all directories\n"
            "1. Create/Sign a wallet\n"
            "2. Check a balance\n"
            "3. Create a transaction\n"
            "4. Send/Receive transations to a Miner\n"
            "5. Create a block\n"
            "6. Exit"
        )
        print(f"{'':=^40}\n")

        option = input("Enter your option: ")
        choice = option
        if option == "0":
            remove_dir()
            print("All directories removed")
            break
        elif option == "1":
            user_name = input("Enter your name: ")
            user_exists = exists(join(PRIVATE_KEY_DIR, f"{user_name}.pem"))
            user_password = input("Enter your password: ")
            if not user_exists:
                wallet.create_new_key(user_name, user_password)
        elif option == "2":
            wallet.check_balance()
        elif option == "3":
            recipient_list = scan_files(PUBLIC_KEY_DIR)
            recipient = list_files(recipient_list)
            amount = input("Enter the amount: ")
            tx = Transaction(user_name, recipient, amount, None)
            tx.process()
        elif option == "4":
            node = Node(user_name)
            node.process()
            option = choice
        elif option == "5":
            block = Block(user_name)
            block.process()
        elif option == "6":
            print("Goodbye!")
            break
        else:
            print("\nInvalid option")
        option = choice


if __name__ == "__main__":
    main()

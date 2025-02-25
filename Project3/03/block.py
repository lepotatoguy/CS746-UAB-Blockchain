from node import Node
from transaction import Transaction
from utils import *
from utxo import UTXO


class Block:
    def __init__(self, recipient=None):
        self.recipient = recipient
        self.utxo = UTXO()

    # add json object transation
    def add_transaction2dict(self, transaction_file):
        with open(transaction_file, "r") as f:
            transaction_data = load(f)
        return transaction_data

    # create blocks
    def save_transaction2block(self, block_hash, transaction_data):
        block_filename = f"{block_hash}.json"
        block_file_path = join(BLOCK_DIR, block_filename)
        create_json_file(block_file_path, transaction_data)

    # check if it's a transaction
    def is_utxo(self, transaction_data):
        return transaction_data["from"] == transaction_data["to"]

    # check if it's a coinbaseTx
    def is_miner(self, transaction_data):
        return transaction_data["from"] == "Miner"

    # move transactions from transaction dir to utxo dir
    def move_transaction2utxo(self, transaction_file):
        rename(transaction_file, join(UTXO_DIR, basename(transaction_file)))

    # create blocks
    def create_block(self, previous_block_hash):
        # get a transaction list and sort them in time creation
        transaction_files = [
            join(TRANSACTION_DIR, f) for f in scan_files(TRANSACTION_DIR)
        ]
        transaction_files.sort(key=lambda x: getmtime(x))

        # block format
        block_data = {
            "height": self.get_next_block_height(),
            "timestamp": time(),
            "previous_block_hash": previous_block_hash,
            "hash": None,
            "transactions": [],
        }

        # generate transations
        for transaction_file in transaction_files:
            transaction_data = self.add_transaction2dict(transaction_file)

            if self.is_utxo(transaction_data):
                self.move_transaction2utxo(transaction_file)
                continue
            # append transations to block
            block_data["transactions"].append(transaction_data)

            # move transations from transaction dir to processed_tx dir
            processed_tx_path = join(PROCESSED_TX_DIR, basename(transaction_file))
            create_json_file(processed_tx_path, transaction_data)

            if self.is_miner(transaction_data):
                # if it's coinbaseTx, move it from transaction dir to utxo dir
                # b/c it's a mining reward
                self.move_transaction2utxo(transaction_file)
            else:
                remove(transaction_file)

        # merkle tree for hash
        block_hash = merkle_tree_hash_root(block_data)
        block_data["hash"] = block_hash

        # save transaction to block
        self.save_transaction2block(block_hash, block_data)
        return block_data

    def get_next_block_height(self):
        # get the height of blocks by counting .json block files
        blocks = scan_files(BLOCK_DIR)
        return len(blocks)

    def get_previous_block_hash(self):
        # get previous block hash by reverse sorting blocks
        # first block is the recent created block
        block_files = [f for f in scan_files(BLOCK_DIR)]

        if not block_files:
            return "NA"

        block_files.sort(key=lambda x: getmtime(join(BLOCK_DIR, x)), reverse=True)

        most_recent_block_path = join(BLOCK_DIR, block_files[0])
        with open(most_recent_block_path, "r") as f:
            block_data = load(f)
        return block_data["hash"]

    def coinbase_process(self):
        # create coinbaseTx
        coinbase = Transaction("Miner", self.recipient, 0, True)
        coinbase.process()

    def process(self):
        # check if there are enough transactions to create blocks
        if len(scan_files(TRANSACTION_DIR)) < 3:
            print(f"Insufficient Transactions")
            exit()
        # create coinbaseTx
        self.coinbase_process()

        # get the previous block hash to create new blocks
        previous_block_hash = self.get_previous_block_hash()

        # create blocks
        current_block_data = self.create_block(previous_block_hash)

        # send blocks to other miners
        node = Node()
        node.send_data2peers(current_block_data)

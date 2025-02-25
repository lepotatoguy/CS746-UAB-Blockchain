import json
import socket
import struct

from utils import *

PEERS = [("127.0.0.1", 5555), ("127.0.0.1", 5556)]


class Node:
    def __init__(self, user_name=None, port=None):
        self.user_name = user_name

    # read transactions to send other miners
    def read_transactions(self):
        for filename in scan_files(PENDING_DIR):
            if filename.endswith(".json"):
                file_path = join(PENDING_DIR, filename)
                with open(file_path, "r") as f:
                    content = f.read()
                transaction_data = loads(content)
                transaction_data["filename"] = filename
                signature = transaction_data["signature"]
                if self.verify(transaction_data, signature):
                    self.process_new_transaction(transaction_data)

    # generate data
    def recvall(self, sock, n):
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    # get transactions/blocks from other peers
    def listen_for_incoming_connections(self):
        while True:
            host = "127.0.0.1"
            port = int(input("Enter your port: "))
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((host, port))
                    s.listen()
                    print(
                        f"Node started on {host}: {port}. Listening for incoming connections..."
                    )
                    while True:
                        conn, addr = s.accept()
                        with conn:
                            print(f"Connected by {addr}")

                            # Handle incoming messages with a size header
                            raw_msglen = self.recvall(conn, 4)
                            if not raw_msglen:
                                break
                            msglen = struct.unpack(">I", raw_msglen)[0]

                            received_data = self.recvall(conn, msglen)
                            if not received_data:
                                break

                            # Attempt to deserialize the received data
                            try:
                                data = json.loads(received_data.decode("utf-8"))
                                # Determine if it is a transaction or a block
                                if (
                                    "transactions" in data
                                ):  # Simple check to differentiate block from transaction
                                    # Handle block
                                    self.process_new_block(data)
                                else:
                                    # Handle transaction
                                    self.process_new_transaction(data)
                                    print(
                                        f"Transaction from {addr} processed and saved."
                                    )
                                    conn.sendall(b"Transaction received and processed")
                            except json.JSONDecodeError:
                                print(f"Received data from {addr} was not valid JSON.")

                            # TODO
                            # add a functionality for processing transactions (i.e., stxo, utxo) to create blocks
                            # add a functionality for creating a block on miner's side
            except Exception as e:
                print(f"{e}")

    # create blocks
    def process_new_block(self, block_data):
        block_file_path = join(BLOCK_DIR, f"{block_data['hash']}.json")
        create_json_file(block_file_path, block_data)
        print(f"Block {block_data['hash']} processed and saved.")

    # create/send transactions and remove processed transactions
    def process_new_transaction(self, transaction):
        transaction_file_path = join(TRANSACTION_DIR, transaction["filename"])
        # check if files exist
        if exists(transaction_file_path):
            print("Transaction already exists.")
            return
        else:
            # send transations to other miners
            self.send_data2peers(transaction)

            filename = transaction.pop("filename", None)

            # create transactions
            create_json_file(transaction_file_path, transaction)
            print("Transaction processed and saved.")

            # delete processed transactions
            if filename:
                pending_file_path = join(PENDING_DIR, filename)
                if exists(pending_file_path):
                    remove(pending_file_path)
                    print(f"Pending transaction file {filename} deleted.")

    # send transations/blocks to other miners
    def send_data2peers(self, data):
        serialized_transaction = encode(dumps(data))
        message = (
            struct.pack(">I", len(serialized_transaction)) + serialized_transaction
        )
        for peer in PEERS:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(peer)
                    s.sendall(message)
                    print(f"Transaction sent to {peer}")
            except Exception as e:
                print(f"Error sending transaction to {peer}: {e}")

    # verify data with its signature
    def verify(self, transaction, signature):
        genuine_message = {
            "timestamp": transaction["timestamp"],
            "from": transaction["from"],
            "to": transaction["to"],
            "amount": transaction["amount"],
        }
        message = dumps(genuine_message)
        try:
            verify_message(message, self.user_name, bytes.fromhex(signature))
            return True
        except Exception as e:
            print(f"Error in verification: {e}")
            return False

    def process(self):
        while True:
            print(f"\n{' Node ':=^40}")
            print(
                "1. Send transactions to Miners\n"
                "2. Wait for communications\n"
                "3. Return to the menu"
            )
            print(f"{'':=^40}\n")
            option = input("Enter your option: ")
            if option == "1":
                self.read_transactions()
            elif option == "2":
                self.listen_for_incoming_connections()
            elif option == "3":
                break

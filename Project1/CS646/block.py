import json
import hashlib
import time
import os
import glob
import transaction

# Directories
TRANSACTION_DIR = 'pending/'
PROCESSED_DIR = 'processed/'
BLOCK_DIR = 'blocks/'


def hashing(data):
    # SHA-256 hash
    return hashlib.sha256(data.encode()).hexdigest()


def get_previous_block_hash():
    # Get the previous block hash from the last block json file in the block directory
    block_files = sorted(glob.glob(BLOCK_DIR + "*.json"))
    if block_files:
        last_block_file = block_files[-1]
        with open(last_block_file, 'r') as f:
            last_block = json.load(f)
            return last_block["header"]["hash"]
    return "NA"


def get_block_height():
    # Get the block height of the number of json files in the block directory
    block_files = sorted(glob.glob(BLOCK_DIR + "*.json"))
    return len(block_files)


def add_transactions():
    # Add all transaction files to a list
    transactions = []
    for trans_file in glob.glob(TRANSACTION_DIR + "*.json"):
        with open(trans_file, 'r') as f:
            transaction = json.load(f)
            transactions.append({
                "hash": os.path.basename(trans_file).replace(".json", ""),
                "content": transaction
            })
        os.rename(trans_file, PROCESSED_DIR +
                  f"{os.path.basename(trans_file)}")
        print(f"{trans_file} is moved into the processed directory!")
    return transactions


def add_transactions_into_JSON(transactions, timestamp, previous_block_hash):
    # Convert the dictionary to JSON string
    body = {"transactions": transactions}
    body_string = json.dumps(body, separators=(',', ':'))

    header = {
        "height": get_block_height(),
        "timestamp": timestamp,
        "previousblock": previous_block_hash,
        "hash": hashing(body_string)  # save the hash in SHA-256
    }

    block = {
        "header": header,
        "body": body
    }

    return (header, block)


def create_dir():
    # Create 'blocks' and 'processed' directory if they do not exist
    if not os.path.exists(TRANSACTION_DIR):
        os.makedirs(TRANSACTION_DIR)
    if not os.path.exists(BLOCK_DIR):
        os.makedirs(BLOCK_DIR)
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)


def create_block(header, block):
    # Create a block.json
    block_filename = BLOCK_DIR + f"{header['hash']}.json"

    with open(block_filename, 'w') as f:
        json.dump(block, f, separators=(',', ':'), indent=4)
    print(f"{header['hash']}.json has been created!")


def delete_files(dir):
    # Delete all files in a directory
    files = glob.glob(dir + '*.json')

    for file in files:
        try:
            os.remove(file)
        except OSError as e:
            print("Error: %s : %s" % (file, e.strerror))
    print(f"All files in the {dir[:-1]} have been removed!")


def main():
    # Create 'processed' directory and 'block' directory
    create_dir()

    # Make a list of transaction files
    transactions = add_transactions()

    # Get timestamp
    timestamp = int(time.time())

    # Get the previous block hash
    previous_block_hash = get_previous_block_hash()

    # Add all transaction files to a .json block file
    header, block = add_transactions_into_JSON(
        transactions, timestamp, previous_block_hash)

    # Create a block .json with the height and the previous hash
    create_block(header, block)


if __name__ == '__main__':
    while True:
        option = input(
            "\n---------------------------------------------\n"            
            "1. Create block\n"
            "2. Delete all files in the pending directory\n"
            "3. Delete all files in the block directory\n"
            "4. Delete all files in the processed directory\n"
            "5. Exit"
            "\n---------------------------------------------\n"
            "Enter your option: ")
        
        if option == '1':
            main()
        elif option == '2':
            delete_files(TRANSACTION_DIR)
        elif option == '3':
            delete_files(BLOCK_DIR)
        elif option == '4':
            delete_files(PROCESSED_DIR)
        elif option == '5':
            break

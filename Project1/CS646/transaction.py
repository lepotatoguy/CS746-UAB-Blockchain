import json
import hashlib
import time
import os

# Transaction directory
TRANSACTION_DIR = 'pending/'

def hashing(data):    
    # SHA-256 hash
    return hashlib.sha256(data.encode()).hexdigest()

def save_to_JSON(data, dir, filename):
    # Save information in a .json file
    with open(dir+filename, 'w') as file:
        json.dump(data, file, separators=(',', ':'), indent=4)            
    
    print(f"{filename} has been created!")
    
def convert_to_JSON(transaction):
    # Convert the dictionary to JSON string
    transaction_string = json.dumps(transaction, separators=(',', ':'))
    
    # Convert the string to SHA-256 hash
    json_file = hashing(transaction_string)
    return json_file

def create_dir():
    # Create the directory if not exist
    if not os.path.exists(TRANSACTION_DIR):
        os.makedirs(TRANSACTION_DIR)    

def get_info():
    # Get information
    timestamp = int(time.time())
    from_acc = input("\nEnter the sender: ")
    to_acc = input("Enter the receiver: ")
    amount = int(input("Enter the amount: "))

    transaction = {
        "timestamp": timestamp,
        "from": from_acc,
        "to": to_acc,
        "amount": amount
    }
    
    return transaction

def main():
    # Get information of time, sender, recipant, and amount    
    transaction = get_info()
    
    # Convert the info to JSON
    json_file = convert_to_JSON(transaction)
    
    # Create 'transaction' directory to store transaction files if not exists
    create_dir()
    
    # Save all the information in a .json file
    save_to_JSON(transaction, TRANSACTION_DIR, f"{json_file}.json")

if __name__ == '__main__':
    main()

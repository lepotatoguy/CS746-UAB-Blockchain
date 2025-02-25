from glob import glob
from hashlib import sha256
from json import dump, dumps, load, loads
from os import mkdir, remove, rename, scandir
from os.path import basename, exists, getmtime, getsize, isfile, join
from shutil import rmtree
from time import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)
from merkle_tree import *

PRIVATE_KEY_DIR = "private_key"
PUBLIC_KEY_DIR = "public_key"
ADDRESS_DIR = "address"
UTXO_DIR = "utxo"
PENDING_DIR = "pending"
TRANSACTION_DIR = "transaction"
PROCESSED_TX_DIR = "processed_tx"
BLOCK_DIR = "block"
DIRS = [
    PRIVATE_KEY_DIR,
    PUBLIC_KEY_DIR,
    ADDRESS_DIR,
    UTXO_DIR,
    PENDING_DIR,
    TRANSACTION_DIR,
    PROCESSED_TX_DIR,
    BLOCK_DIR,
]

""" TIME """


def get_time():
    return int(time())


""" HASH """


def hash(string):
    return sha256(encode(string)).hexdigest()


def encode(string):
    code = "UTF-8"  # default value of encode is utf-8, but just to make it sure.
    return string.encode(code)


def decode(bytes_string):
    code = "UTF-8"
    return bytes_string.decode(code)


def string2hash(*args):
    h = sha256()
    for arg in args:
        encoded_h = encode(arg)
        h.update(encoded_h)
    return h.hexdigest()


def dict2json(dic):
    dic_string = dumps(dic)
    json_file = hash(dic_string)
    return json_file


def merkle_tree_hash_root(transactions):
    merkle_tree = MerkleTree(transactions)
    root_hash = merkle_tree.create_merkle_tree()
    return root_hash


""" FILES """


def create_file(path, data):
    if not exists(path):
        with open(path, "w") as f:
            f.write(data)


def create_bytes_file(path, data):
    if not exists(path):
        with open(path, "wb") as f:
            f.write(data)
        print(f"{path} has been created.")


def create_json_file(path, data):
    with open(path, "w") as f:
        dump(data, f, separators=(",", ":"), indent=4)
    print(f"{path} has been created")


def remove_file(path):
    if isfile(path):
        remove(path)


def list_files(lst):
    print(f"\nChoose a number:")
    n = 1
    for name in lst:
        print(f"{n}. {name}")
        n += 1
    option = input("\nOption: ")
    choice = lst[int(option) - 1]
    return choice


def scan_files(dir):
    file_list = []
    with scandir(dir) as entries:
        for entry in entries:
            if entry.is_file() and not entry.name.startswith(
                "."
            ):  # and entry.name.endswith('.json'):
                file_list.append(entry.name)
    return file_list


def read_files(dir):
    transaction_list = []
    with scandir(dir) as entries:
        for entry in entries:
            if entry.is_file() and not entry.name.startswith(
                "."
            ):  # and entry.name.endswith('.json'):
                with open(join(dir, entry.name), "r") as f:
                    transaction = load(f)
                    transaction_list.append(transaction)
    return transaction_list


""" DIRECTORIES """


def create_dir():
    for dir in DIRS:
        if not exists(dir):
            mkdir(dir)


def remove_dir(dir="."):
    with scandir(dir) as entries:
        for entry in entries:
            if entry.is_dir():
                rmtree(entry)


""" KEYS """


def load_private_key(user_name, user_password):
    private_key_path = join(PRIVATE_KEY_DIR, f"{user_name}.pem")
    with open(private_key_path, "rb") as f:
        private_key = load_pem_private_key(
            f.read(), password=user_password.encode("utf-8")
        )
    return private_key


def load_public_key(user_name):
    public_key_path = join(PUBLIC_KEY_DIR, f"{user_name}")
    with open(public_key_path, "rb") as f:
        public_key = load_pem_public_key(f.read(), backend=default_backend())
    return public_key


""" ADDRESSES """


def publickey2address(public_key):
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.PKCS1
    )
    decode_public_key = public_key_bytes.decode()
    public_key_address = sha256(decode_public_key.encode()).hexdigest()
    return public_key_address


def create_address(user_name):
    public_key = load_public_key(user_name)
    address = publickey2address(public_key)
    content = {"name": user_name, "address": address}
    json_content = dumps(content, separators=(",", ":"), indent=4)
    address_path = join(ADDRESS_DIR, user_name)
    create_file(address_path, json_content)
    print(f"{content['name']}'s address: {content['address']}")


""" VALIDATION """


def sign_message(data, private_key):
    message = encode(dumps(data))
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return signature


def verify_message(message, public_key_name, signature):
    try:
        public_key_path = join(PUBLIC_KEY_DIR, public_key_name)
        with open(public_key_path, "rb") as f:
            pub_key = f.read()
        public_key = load_pem_public_key(pub_key, default_backend())
        public_key.verify(
            signature,
            message.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except:
        return False

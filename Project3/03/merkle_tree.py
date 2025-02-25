from hashlib import sha256
from json import dumps


class MerkleNode:
    def __init__(self, hash_value: str, left=None, right=None):
        self.hash_value = hash_value
        self.left = left
        self.right = right


class MerkleTree:
    def __init__(self, transactions):
        self.leaves = []
        self.transactions = transactions

    # add leaf to tree
    def add_leaf(self, data):
        leaf_hash = self.compute_hash(data)
        self.leaves.append(MerkleNode(leaf_hash))

    # hash
    def compute_hash(self, data):
        json_data = dumps(data, sort_keys=True)
        return sha256(json_data.encode("utf-8")).hexdigest()

    # generate tree
    def build_tree(self):
        nodes = self.leaves
        if len(nodes) == 0:
            raise ValueError("No leaves to build a tree")

        while len(nodes) > 1:
            if len(nodes) % 2 != 0:
                nodes.append(nodes[-1])

            new_nodes = []
            for i in range(0, len(nodes), 2):
                combined_hash = self.compute_hash(
                    nodes[i].hash_value + nodes[i + 1].hash_value
                )
                new_node = MerkleNode(combined_hash, left=nodes[i], right=nodes[i + 1])
                new_nodes.append(new_node)

            nodes = new_nodes

        self.root = nodes[0]

    # get root hash
    def get_root_hash(self):
        if not hasattr(self, "root"):
            raise ValueError("Merkle tree has not been built yet")
        return self.root.hash_value

    # create merkle tree
    def create_merkle_tree(self):
        self.add_leaf(self.transactions)
        self.build_tree()
        root_hash = self.get_root_hash()
        return root_hash

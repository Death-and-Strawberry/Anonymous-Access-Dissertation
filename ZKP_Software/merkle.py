# merkle.py
from circomlibpy.poseidon import PoseidonHash
from typing import List, Tuple


poseidon = PoseidonHash()


DEPTH = 8
EMPTY = 0  # field element 0 for empty leaves

#circomlibpy does not have a curve order built in
FIELD_ORDER = 21888242871839275222246405745257275088548364400416034343698204186575808495617

    
def _to_field(v) -> int:
    """
    Normalize v into a BN254 field integer.
    Accepts: int, bytes, str.
    """

    if isinstance(v, int):
        return v % FIELD_ORDER  # reduce mod field prime
    if isinstance(v, bytes):
        return int.from_bytes(v, "big") % FIELD_ORDER
    if isinstance(v, str):
        return _to_field(v.encode())
    # fallback: stringify and encode
    return _to_field(str(v).encode())

def poseidon_hash(values) -> int:
    """
    Poseidon hash using circomlibpy.poseidon.
    Accepts a single value or a list/tuple of values.
    Returns an integer field element (BN254 scalar).
    """

    if not isinstance(values, (list, tuple)):
        values = [values]
    field_vals = [_to_field(v) for v in values]
    return poseidon.hash(len(field_vals), field_vals)


class MerkleTree:
    """
    Simple binary Merkle tree using Poseidon hash over field integers.
    """
    
    def __init__(self, leaves: List[int], depth: int = DEPTH):
        self.depth = depth
        self.size = 1 << depth
        normalized = [_to_field(l) for l in leaves]
        if len(normalized) > self.size:
            raise ValueError("Too many leaves for depth")
        normalized += [EMPTY] * (self.size - len(normalized)) # add 0's for the empty part of the tree
        self.leaves = normalized
        self._build_tree()

    def _build_tree(self):
        self.layers = [self.leaves[:]]
        cur = self.leaves
        while len(cur) > 1:
            nxt = []
            for i in range(0, len(cur), 2):
                left = cur[i]
                right = cur[i+1]
                parent = poseidon_hash([left, right])
                nxt.append(parent)
            self.layers.append(nxt)
            cur = nxt
        self.root = self.layers[-1][0]

    def insert_at(self, index: int, leaf_value):
        self.leaves[index] = _to_field(leaf_value)
        self._build_tree()

    def remove_at(self, index: int):
        self.leaves[index] = EMPTY
        self._build_tree()

    def get_root(self) -> int:
        return self.root

    def get_proof(self, index: int) -> Tuple[List[int], List[int]]:
        """
        Returns (pathElements, pathIndices)
        pathElements: list of sibling hashes (field ints)
        pathIndices: list of bits (0 if current node is left, 1 if right)
        """
        path = []
        indices = []
        idx = index 
        for d in range(self.depth):
            sibling = idx ^ 1
            sibling_hash = self.layers[d][sibling]
            path.append(sibling_hash)
            indices.append(idx & 1)
            idx >>= 1
        return path, indices

#Safeguard to ensure input to the hash is passed exactly as defined below
def poseidon_hash_two(a: int, b: int) -> int:
    return poseidon.hash(2, [a, b])


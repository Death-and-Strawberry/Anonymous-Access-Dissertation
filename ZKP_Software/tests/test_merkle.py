# tests/test_merkle.py
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from merkle import (
    MerkleTree, 
    poseidon_hash, 
    poseidon_hash_two, 
    _to_field, 
    DEPTH, 
    EMPTY, 
    FIELD_ORDER
)

# Fixtures for common test data
@pytest.fixture
def sample_leaves():
    """Provides sample leaves for testing"""

    return [1, 2, 3, 4, 5, 6, 7, 8]

@pytest.fixture
def small_leaves():
    """Provides a small set of leaves"""

    return [10, 20]

@pytest.fixture
def field_elements():
    """Different values for test cases"""

    return {
        'int': 12345,
        'bytes': b'\x04\x04\x04\x04',
        'string': "test",
        'large_int': FIELD_ORDER + 100,  # Should be reduced mod FIELD_ORDER
        'zero': 0,
        'max_field': FIELD_ORDER - 1
    }

@pytest.fixture
def merkle_tree(sample_leaves):
    """Provides a pre-built Merkle tree"""

    return MerkleTree(sample_leaves)

class TestFieldOperations:
    """Test field element normalisation and basic operations"""
    
    def test_to_field_with_int(self, field_elements):
        """Test _to_field with integer inputs"""

        # Normal integer
        result = _to_field(field_elements['int'])
        assert result == field_elements['int']
        assert isinstance(result, int)
        
        # Large integer should be reduced
        result = _to_field(field_elements['large_int'])
        assert result == (field_elements['large_int'] % FIELD_ORDER)
        assert result < FIELD_ORDER
        
        # Zero
        result = _to_field(field_elements['zero'])
        assert result == 0
        
        # Maximum field element
        result = _to_field(field_elements['max_field'])
        assert result == FIELD_ORDER - 1

    def test_to_field_with_bytes(self, field_elements):
        """Test _to_field with bytes inputs"""

        result = _to_field(field_elements['bytes'])
        expected = int.from_bytes(field_elements['bytes'], "big") % FIELD_ORDER
        assert result == expected
        assert isinstance(result, int)

    def test_to_field_with_string(self, field_elements):
        """Test _to_field with string inputs"""

        result = _to_field(field_elements['string'])
        expected = int.from_bytes(field_elements['string'].encode(), "big") % FIELD_ORDER
        assert result == expected
        assert isinstance(result, int)

    def test_to_field_with_other_types(self):
        """Test _to_field with other types (should stringify first)"""

        # List should be stringified
        test_list = [1, 2, 3]
        result = _to_field(test_list)
        expected = _to_field(str(test_list))
        assert result == expected
        
        # Float should be stringified
        test_float = 3.14
        result = _to_field(test_float)
        expected = _to_field(str(test_float))
        assert result == expected

class TestPoseidonHash:
    """Test Poseidon hash functions"""
    
    def test_poseidon_hash_single_value(self):
        """Test poseidon_hash with a single value"""
        value = 42
        result = poseidon_hash(value)
        assert isinstance(result, int)
        assert result >= 0
        assert result < FIELD_ORDER
        
        # Should be same as passing list with one element
        result2 = poseidon_hash([value])
        assert result == result2

    def test_poseidon_hash_multiple_values(self):
        """Test poseidon_hash with multiple values"""
        values = [1, 2, 3, 4]
        result = poseidon_hash(values)
        assert isinstance(result, int)
        assert result >= 0
        assert result < FIELD_ORDER
        
        # Should be deterministic
        result2 = poseidon_hash(values)
        assert result == result2
        
        # Different order should give different result
        different_order = [4, 3, 2, 1]
        result3 = poseidon_hash(different_order)
        assert result != result3

    def test_poseidon_hash_two(self):
        """Test the specific poseidon_hash_two function"""
        a, b = 100, 200
        result = poseidon_hash_two(a, b)
        assert isinstance(result, int)
        assert result >= 0
        assert result < FIELD_ORDER
        
        # Should be same as general poseidon_hash with 2 elements
        result2 = poseidon_hash([a, b])
        assert result == result2
        
        # Should be deterministic
        result3 = poseidon_hash_two(a, b)
        assert result == result3
        
        # Test Order
        result4 = poseidon_hash_two(b, a)
        assert result != result4

    def test_poseidon_hash_with_mixed_types(self):
        """Test poseidon_hash with mixed input types"""

        values = [42, b'\x01\x02', "test"]
        result = poseidon_hash(values)
        assert isinstance(result, int)
        assert result >= 0
        assert result < FIELD_ORDER

class TestMerkleTree:
    """Test MerkleTree functionality"""
    
    def test_merkle_tree_initialization(self, sample_leaves):
        """Test basic Merkle tree initialization"""
        tree = MerkleTree(sample_leaves)
        
        assert tree.depth == DEPTH
        assert tree.size == (1 << DEPTH)
        assert len(tree.leaves) == tree.size
        assert tree.leaves[:len(sample_leaves)] == sample_leaves
        
        # Remaining leaves should be EMPTY (0)
        for i in range(len(sample_leaves), tree.size):
            assert tree.leaves[i] == EMPTY
        
        # Should have layers
        assert len(tree.layers) == DEPTH + 1  # leaf layer + internal layers
        assert tree.root is not None
        assert isinstance(tree.root, int)

    def test_merkle_tree_custom_depth(self, small_leaves):
        """Test Merkle tree with custom depth"""

        custom_depth = 3
        tree = MerkleTree(small_leaves, depth=custom_depth)
        
        assert tree.depth == custom_depth
        assert tree.size == (1 << custom_depth)
        assert len(tree.leaves) == tree.size
        assert len(tree.layers) == custom_depth + 1

    def test_merkle_tree_too_many_leaves(self):
        """Test error when too many leaves for the depth"""

        depth = 2  # Can only hold 4 leaves
        leaves = [1, 2, 3, 4, 5]
        
        with pytest.raises(ValueError, match="Too many leaves for depth"):
            MerkleTree(leaves, depth=depth)

    def test_merkle_tree_deterministic(self, sample_leaves):
        """Test that tree construction is deterministic"""

        tree1 = MerkleTree(sample_leaves)
        tree2 = MerkleTree(sample_leaves)
        
        assert tree1.root == tree2.root
        assert tree1.leaves == tree2.leaves
        assert len(tree1.layers) == len(tree2.layers)
        
        for i in range(len(tree1.layers)):
            assert tree1.layers[i] == tree2.layers[i]

    def test_get_root(self, merkle_tree):
        """Test get_root method"""

        root = merkle_tree.get_root()
        assert root == merkle_tree.root
        assert isinstance(root, int)
        assert root >= 0

    def test_get_proof_valid_indices(self, merkle_tree, sample_leaves):
        """Test get_proof with valid indices"""

        for i in range(len(sample_leaves)):
            path_elements, path_indices = merkle_tree.get_proof(i)
            
            assert len(path_elements) == DEPTH
            assert len(path_indices) == DEPTH

            for elements in path_elements:
                assert isinstance(elements, int)
                assert elements >= 0
            
            # All path indices should be 0 or 1
            for idx in path_indices:
                assert idx in [0, 1]

    def test_get_proof_different_indices_different_proofs(self, merkle_tree):
        """Test that different indices produce different proofs"""

        proof1 = merkle_tree.get_proof(0)
        proof2 = merkle_tree.get_proof(1)
        
        # At least one element should be different
        assert proof1 != proof2

    def test_insert_at(self, sample_leaves):
        """Test insert_at functionality"""

        tree = MerkleTree(sample_leaves)
        original_root = tree.root
        
        # Insert new value
        new_value = 999
        insert_index = 2
        tree.insert_at(insert_index, new_value)
        
        # Root should change
        assert tree.root != original_root
        
        # Leaf should be updated
        assert tree.leaves[insert_index] == new_value
        
        # Check if the rest of the leaves are still the same
        for i, original_leaf in enumerate(sample_leaves):
            if i != insert_index and i < len(sample_leaves):
                assert tree.leaves[i] == original_leaf

    def test_remove_at(self, sample_leaves):
        """Test remove_at functionality"""

        tree = MerkleTree(sample_leaves)
        original_root = tree.root
        
        # Remove value
        remove_index = 1
        tree.remove_at(remove_index)
        
        # Root should change (unless the leaf == EMPTY)
        if sample_leaves[remove_index] != EMPTY:
            assert tree.root != original_root
        
        # Leaf should be EMPTY
        assert tree.leaves[remove_index] == EMPTY


    def test_merkle_tree_with_field_normalization(self):
        """Test whether tree can handle field normalisation"""

        leaves = [
            42,
            b'\x01\x02',
            "test",
            FIELD_ORDER + 5 
        ]
        
        tree = MerkleTree(leaves)
        
        for leaf in tree.leaves[:len(leaves)]:
            assert isinstance(leaf, int)
            assert 0 <= leaf < FIELD_ORDER

    def test_empty_tree(self):
        """Test tree with no leaves"""

        tree = MerkleTree([])
        
        # All leaves should == EMPTY
        for leaf in tree.leaves:
            assert leaf == EMPTY
        
        assert isinstance(tree.root, int)

    def test_single_leaf_tree(self):
        """Test tree with single leaf"""

        tree = MerkleTree([42])
        
        assert tree.leaves[0] == 42
        for i in range(1, tree.size):
            assert tree.leaves[i] == EMPTY
        
        # Proof of the single leaf
        path_elements, path_indices = tree.get_proof(0)
        assert len(path_elements) == DEPTH
        assert len(path_indices) == DEPTH

class TestMerkleProofVerification:
    """Test Merkle proof verification logic"""
    
    def test_proof_reconstruction(self, merkle_tree, sample_leaves):
        """Test that we can reconstruct root from proof (manual verification)"""

        # This tests the mathematical correctness of proofs
        leaf_index = 2
        leaf_value = sample_leaves[leaf_index]
        path_elements, path_indices = merkle_tree.get_proof(leaf_index)
        
        # Manually compute root from proof
        current_hash = leaf_value
        for i in range(len(path_elements)):
            sibling = path_elements[i]
            if path_indices[i] == 0:  # current node is left child
                current_hash = poseidon_hash_two(current_hash, sibling)
            else:  # current node is right child
                current_hash = poseidon_hash_two(sibling, current_hash)
        
        # Should match the actual root
        assert current_hash == merkle_tree.root

    def test_proof_for_all_leaves(self, merkle_tree, sample_leaves):
        """Test that proofs work for all leaves"""
        
        for i in range(len(sample_leaves)):
            leaf_value = sample_leaves[i]
            path_elements, path_indices = merkle_tree.get_proof(i)
            
            # Reconstruct root
            current_hash = leaf_value
            for j in range(len(path_elements)):
                sibling = path_elements[j]
                if path_indices[j] == 0:
                    current_hash = poseidon_hash_two(current_hash, sibling)
                else:
                    current_hash = poseidon_hash_two(sibling, current_hash)
            
            assert current_hash == merkle_tree.root
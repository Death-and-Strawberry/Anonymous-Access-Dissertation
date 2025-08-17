# test_create_bbs_proof.py
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bbs.sign import issue_credentials
from bbs.create_bbs_proof import create_bbs_selective_proof, verify_bbs_proof

@pytest.fixture
def sample_attributes():
    """Provides sample attributes for tests"""

    attributes = {
        "name": "Alice",
        "age": "30",
        "nationality": "Wonderland"
    }

    return attributes

def test_create_and_verify_bbs_proof(sample_attributes):
    """test attributes to issue and selectively disclose"""
 
    revealed_fields = ["name", "age"]  # Selectively reveal name and age (would not choose these in a real scenario which never discloses PII)
    
    signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(sample_attributes)
    

    bbs_proof, revealed_attrs_bytes, bbs_pub, nonce, merkle_proof, returned_serial, returned_issuer_id, leaf_index = create_bbs_selective_proof(
        signature, keypair, sample_attributes, revealed_fields, tree, serial, issuer_id, all_keys
    )
    
    assert bbs_proof is not None
    assert isinstance(revealed_attrs_bytes, dict)
    assert isinstance(bbs_pub, bytes)
    assert isinstance(nonce, bytes)
    assert isinstance(merkle_proof, tuple)
    assert len(merkle_proof) == 2  # (pathElements, pathIndices)
    assert returned_serial == serial
    assert returned_issuer_id == issuer_id
    assert isinstance(leaf_index, int)
    
    # Check that revealed attributes are in bytes format as expected
    expected_revealed = {}
    for k in revealed_fields:
        expected_revealed[k] = str(sample_attributes[k]).encode()
    assert revealed_attrs_bytes == expected_revealed
    
    # Verify the proof
    message_count = len(all_keys) + 1  # all_keys + commitment
    
    is_valid = verify_bbs_proof(
        bbs_proof=bbs_proof,
        revealed_attrs=revealed_attrs_bytes,
        public_key=bbs_pub,
        nonce=nonce,
        message_count=message_count
    )
    assert is_valid is True

def test_create_and_verify_bbs_proof_with_commitment_revealed(sample_attributes):
    """Test case where commitment is also revealed"""

    revealed_fields = ["name", "commitment"]  # Reveal name and commitment

    signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(sample_attributes)

    bbs_proof, revealed_attrs_bytes, bbs_pub, nonce, merkle_proof, returned_serial, returned_issuer_id, leaf_index = create_bbs_selective_proof(
        signature, keypair, sample_attributes, revealed_fields, tree, serial, issuer_id, all_keys
    )
    
    # Check that revealed attributes include commitment as bytes
    assert "name" in revealed_attrs_bytes
    assert "commitment" in revealed_attrs_bytes
    assert revealed_attrs_bytes["name"] == b"Alice"
    assert isinstance(revealed_attrs_bytes["commitment"], bytes)
    assert len(revealed_attrs_bytes["commitment"]) == 32  # 32-byte commitment
    
    message_count = len(all_keys) + 1
    
    is_valid = verify_bbs_proof(
        bbs_proof=bbs_proof,
        revealed_attrs=revealed_attrs_bytes,
        public_key=bbs_pub,
        nonce=nonce,
        message_count=message_count
    )
    assert is_valid is True

def test_merkle_proof_structure(sample_attributes):
    """Test that merkle proof has correct structure"""

    revealed_fields = ["name"]
    
    signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(sample_attributes)
    
    bbs_proof, revealed_attrs_bytes, bbs_pub, nonce, merkle_proof, returned_serial, returned_issuer_id, leaf_index = create_bbs_selective_proof(
        signature, keypair, sample_attributes, revealed_fields, tree, serial, issuer_id, all_keys
    )
    
    # Check merkle proof structure
    pathElements, pathIndices = merkle_proof
    assert isinstance(pathElements, list)
    assert isinstance(pathIndices, list)
    assert len(pathElements) == len(pathIndices)
    
    # pathElements should contain integers (field elements)
    for element in pathElements:
        assert isinstance(element, int)
    
    # pathIndices should contain 0s and 1s (bits)
    for index in pathIndices:
        assert index in [0, 1]
    
    # leaf_index should be valid
    assert 0 <= leaf_index < len(tree.leaves)
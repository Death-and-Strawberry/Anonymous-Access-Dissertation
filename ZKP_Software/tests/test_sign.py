# test_sign.py
import pytest
from bbs.sign import issue_credentials, verify_attributes
from ursa_bbs_signatures import BlsKeyPair
from merkle import FIELD_ORDER

@pytest.fixture(autouse=True)
def setup_test_data():
    """This runs automatically before each test in this file"""
    # You can put setup code here that runs before every test
    print("Setting up test data...")  # This will run before each test


@pytest.fixture
def sample_attributes():
    """Provides sample attributes for tests"""
    attributes = {
        "name": "Alice",
        "age": "30",
        "nationality": "Wonderland"
    }

    return attributes

def test_field_order_constraint(sample_attributes):
    """Test that serial is properly constrained to field order"""

    signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(sample_attributes)

    # Serial should be less than FIELD_ORDER
    assert serial < FIELD_ORDER
    assert serial >= 0

def test_issue_and_verify_credentials(sample_attributes):
    
    # Issue the credentials
    signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(sample_attributes)
    
    # Test the returned values
    assert signature is not None
    assert isinstance(keypair, BlsKeyPair)
    assert tree is not None
    assert isinstance(serial, int)
    assert isinstance(issuer_id, int)
    assert isinstance(all_keys, list)
    assert set(all_keys) == set(sample_attributes.keys())  
    
    # Verify the credentials
    is_valid = verify_attributes(sample_attributes, signature, keypair, tree, all_keys)
    assert is_valid is True

def test_issue_credentials_with_custom_issuer_id(sample_attributes):

    custom_issuer_id = 777
    
    signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(sample_attributes, custom_issuer_id)
    
    assert issuer_id == custom_issuer_id
    assert isinstance(keypair, BlsKeyPair)
    assert len(all_keys) == len(sample_attributes)
    
    # Verify with the custom issuer ID
    is_valid = verify_attributes(sample_attributes, signature, keypair, tree, all_keys)
    assert is_valid is True

def test_verify_attributes_with_wrong_data(sample_attributes):
    """Test that verification fails with incorrect attributes"""
    
    wrong_attributes = {
        "name": "NotCharlie",  # Wrong name
        "age": 25,
        "nationality": "Underworld"
    }
    
    signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(sample_attributes)
    
    # Should fail with wrong attributes
    is_valid = verify_attributes(wrong_attributes, signature, keypair, tree, all_keys)
    assert is_valid is False

def test_verify_attributes_with_wrong_order(sample_attributes):
    """Test that verification handles attribute ordering correctly"""
    
    signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(sample_attributes)
    
    # Same attributes but different order - should still work because all_keys preserves order
    reordered_attributes = {
        "nationality": "Wonderland",
        "name": "Alice", 
        "age": 30
    }
    
    # This should still pass because all_keys maintains the original order
    is_valid = verify_attributes(reordered_attributes, signature, keypair, tree, all_keys)
    assert is_valid is True

def test_multiple_credentials_different_serials(sample_attributes):
    """Test that different credential issuances produce different serials"""
    
    # Issue credentials twice for the same attributes
    sig1, kp1, tree1, serial1, issuer_id1, keys1 = issue_credentials(sample_attributes)
    sig2, kp2, tree2, serial2, issuer_id2, keys2 = issue_credentials(sample_attributes)
    
    # Ensure serials should be different (random)
    assert serial1 != serial2
    
    assert verify_attributes(sample_attributes, sig1, kp1, tree1, keys1) is True
    assert verify_attributes(sample_attributes, sig2, kp2, tree2, keys2) is True

    
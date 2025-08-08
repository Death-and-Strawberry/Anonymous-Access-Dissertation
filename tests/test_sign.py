
import pytest
from bbs.sign import issue_credentials, verify_attributes
from ursa_bbs_signatures import BlsKeyPair

def test_issue_and_verify_credentials():
    # Example user attributes
    attrs = {
        "name": "Alice",
        "age": 30,
        "citizenship": "Wonderland"
    }

    # Issue the credentials
    signature, keypair = issue_credentials(attrs)

    assert signature is not None
    assert isinstance(keypair, BlsKeyPair)

    # Verify the credentials
    is_valid = verify_attributes(attrs, signature, keypair)

    assert is_valid is True
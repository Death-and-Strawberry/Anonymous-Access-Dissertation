# test_create_bbs_proof.py

import pytest

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bbs.sign import issue_credentials
from bbs.create_bbs_proof import create_bbs_selective_proof, verify_bbs_proof

def test_create_and_verify_bbs_proof():
    # Attributes to issue and selectively disclose
    attrs = {
        "name": "Alice",
        "age": 30,
        "citizenship": "Wonderland"
    }
    revealed_fields = ["name", "age"]  # Selectively reveal name and age

    # Step 1: Issue signature
    signature, keypair = issue_credentials(attrs)

    # Step 2: Create selective disclosure proof
    bbs_proof, revealed_attrs, bbs_pub, nonce = create_bbs_selective_proof(
        signature, keypair, attrs, revealed_fields
    )

    assert bbs_proof is not None
    assert revealed_attrs == {k: attrs[k] for k in revealed_fields}
    assert isinstance(bbs_pub, bytes)
    assert isinstance(nonce, bytes)

    # Step 3: Verify the proof
    is_valid = verify_bbs_proof(
        bbs_proof=bbs_proof,
        revealed_attrs=revealed_attrs,
        public_key=bbs_pub,
        nonce=nonce,
        message_count=len(attrs)
    )

    assert is_valid is True
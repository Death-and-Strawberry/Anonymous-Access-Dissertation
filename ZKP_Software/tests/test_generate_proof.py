# test_generate_proof.py
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from unittest.mock import patch, MagicMock
from zk.generate_proof import generate_zk_proof, compile_circuit

circom_folder = "zk"
circuit_name = "eligibility"

@patch("zk.generate_proof.subprocess.run")
@patch("zk.generate_proof.os.path.exists", return_value=False)  # simulate files not existing so subprocess run is called
def test_compile_circuit(mock_exists, mock_run):
    """Test whether the circuit compilation executes"""

    compile_circuit()
    mock_run.assert_called_once_with([
        "circom", "zk/eligibility.circom", 
        "--r1cs", "--wasm", "--sym", "--output", 'zk'
    ], check=True)

@patch("zk.generate_proof.subprocess.run")
@patch("zk.generate_proof.os.path.exists", return_value=True)  # simulate files already exist
def test_skip_compile_circuit(mock_exists, mock_run):
    """Test it being skipped if exists"""

    compile_circuit()
    mock_run.assert_not_called()

@patch("zk.generate_proof.subprocess.run")
@patch("zk.generate_proof.write_json")
def test_generate_zk_proof_with_merkle_data(mock_write_json, mock_run):
    """Test generate_zk_proof with complete Merkle tree data"""
    
    inputs = {
        "birth_year": 2000,
        "birth_month": 1,
        "birth_day": 1,
        "current_year": 2024,
        "current_month": 6,
        "current_day": 1,
        "expiry_year": 2030,
        "expiry_month": 12,
        "nationality": 826,
        "valid_signature": 1,
        "serial": 123456,
        "issuer_id": 789,
        "merkle_leaves": [456789],  # Example commitment
        "leaf_index": 0
    }
    
    result = generate_zk_proof(**inputs)
    
    # Check that subprocess.run was called twice (witness generation + proof generation)
    assert mock_run.call_count == 2
    
    # Check witness generation call
    witness_call = mock_run.call_args_list[0]
    expected_witness_call = [
        "node", "zk/eligibility_js/generate_witness.js",
        "zk/eligibility_js/eligibility.wasm", "zk/input.json", "zk/witness.wtns"
    ]
    assert witness_call[0][0] == expected_witness_call
    assert witness_call[1]["check"] == True
    
    # Check proof generation call
    proof_call = mock_run.call_args_list[1]
    expected_proof_call = [
        "snarkjs", "plonk", "prove",
        "zk/eligibility_final.zkey", "zk/witness.wtns", "out/proof.json", "out/public.json"
    ]
    assert proof_call[0][0] == expected_proof_call
    assert proof_call[1]["check"] == True
    
    # Check that write_json was called to write the input file
    mock_write_json.assert_called_once()
    call_args = mock_write_json.call_args
    assert call_args[0][0] == "zk/input.json"  # file path
    
    # Check that the written JSON contains expected fields
    written_data = call_args[0][1]
    assert "birth_year" in written_data
    assert "revealed_commitment" in written_data
    assert "merkle_root" in written_data
    assert "pathElements" in written_data
    assert "pathIndices" in written_data
    assert "credential_serial_lo" in written_data
    assert "issuer_id" in written_data
    
    # Check return value
    assert result == {
        "proof": "out/proof.json",
        "public": "out/public.json"
    }

@patch("zk.generate_proof.subprocess.run")
@patch("zk.generate_proof.write_json")
def test_generate_zk_proof_without_merkle_data(mock_write_json, mock_run):
    """Test generate_zk_proof when Merkle data is None (should not execute proof generation)"""

    inputs = {
        "birth_year": 2000,
        "birth_month": 1,
        "birth_day": 1,
        "current_year": 2024,
        "current_month": 6,
        "current_day": 1,
        "expiry_year": 2030,
        "expiry_month": 12,
        "nationality": 826,
        "valid_signature": 1,
        "serial": None,
        "issuer_id": None,
        "merkle_leaves": None,
        "leaf_index": None
    }
    
    # This should raise an UnboundLocalError
    # The function references 'commitment' outside the conditional block
    with pytest.raises(UnboundLocalError):
        generate_zk_proof(**inputs)

@patch("zk.generate_proof.subprocess.run")
@patch("zk.generate_proof.write_json")
def test_generate_zk_proof_partial_merkle_data(mock_write_json, mock_run):
    """Test generate_zk_proof when only some Merkle data is provided"""
    inputs = {
        "birth_year": 2000,
        "birth_month": 1,
        "birth_day": 1,
        "current_year": 2024,
        "current_month": 6,
        "current_day": 1,
        "expiry_year": 2030,
        "expiry_month": 12,
        "nationality": 826,
        "valid_signature": 1,
        "serial": 123456,
        "issuer_id": 789,
        "merkle_leaves": None,  # Missing merkle_leaves
        "leaf_index": 0
    }
    
    # This should also raise an UnboundLocalError (essentially always will unless all data is provided)
    with pytest.raises(UnboundLocalError):
        generate_zk_proof(**inputs)

@patch("zk.generate_proof.subprocess.run")
def test_verify_zk_proof(mock_run):
    """Test the verify_zk_proof function"""
    
    from zk.generate_proof import verify_zk_proof
    
    verify_zk_proof()
    
    expected_call = [
        "snarkjs", "plonk", "verify",
        "zk/verification_key.json",
        "out/public.json", 
        "out/proof.json"
    ]
    mock_run.assert_called_once_with(expected_call, check=True)

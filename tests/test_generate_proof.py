
# tests/test_generate_proof.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import patch
from zk.generate_proof import generate_zk_proof, compile_circuit

circom_folder = "zk"
circuit_name = "eligibility"

@patch("zk.generate_proof.subprocess.run")
@patch("zk.generate_proof.os.path.exists", return_value=False) #simulate files not existing so subprocess run is called, order is bottom up
def test_compile_circuit(mock_exists, mock_run):
    compile_circuit()
    mock_run.assert_called_once_with(["circom", "zk/eligibility.circom", "--r1cs", "--wasm", "--sym", "--output", 'zk'],
        check=True)

@patch("zk.generate_proof.subprocess.run")
def test_skip_compile_circuit(mock_run):
    compile_circuit()
    mock_run.assert_not_called()

@patch("zk.generate_proof.subprocess.run")
def test_generate_zk_proof(mock_run):
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
        "valid_signature": 1
    }
    generate_zk_proof(**inputs)
    mock_run.assert_called_once
    

import subprocess
import os
from pathlib import Path
from utils import write_json
from math import ceil, log2
from merkle import MerkleTree, PoseidonHash, poseidon_hash_two, FIELD_ORDER, DEPTH
from merkle import poseidon_hash_two

circom_folder = "zk"
circuit_name = "eligibility"
wasm_path = f"{circom_folder}/{circuit_name}_js/{circuit_name}.wasm"
input_json = f"{circom_folder}/input.json"
witness_path = f"{circom_folder}/witness.wtns"
zkey_path = f"{circom_folder}/{circuit_name}_final.zkey"
proof_path = "out/proof.json"
public_path = "out/public.json"

poseidon = PoseidonHash()

"""!!"""
def compile_circuit():
    if not os.path.exists(f"{circom_folder}/{circuit_name}.r1cs"):
        print("[Setup] Compiling circom circuit...")
        subprocess.run([
            "circom", f"{circom_folder}/{circuit_name}.circom",
            "--r1cs", "--wasm", "--sym", "--output", circom_folder
        ], check=True)
        print("[Setup] Compilation complete.")
    else:
        print("[Setup] Circuit already compiled.")

# Merkle tree + Poseidon helpers
def poseidon_hash(*values):
    """Hashes a tuple of integers with Poseidon (to match Circom's poseidon)."""
    return poseidon.hash(len(values), list(values))

def build_merkle_root(leaves):
    """
    Builds a Merkle root from a list of [serial, issuer_id] leaves using Poseidon.
    Leaves should be a list of lists, each inner list = [serial, issuer_id].
    """
    if not leaves:
        return 0
    mt = MerkleTree(leaves)
    return mt.root

"""!!"""
def generate_zk_proof(
    birth_year, birth_month, birth_day,
    expiry_year, expiry_month, nationality,
    current_year, current_month, current_day,
    valid_signature,
    serial, issuer_id, merkle_leaves, leaf_index
):
    
    if serial is not None and issuer_id is not None and merkle_leaves is not None and leaf_index is not None:
        
        commitment = poseidon_hash_two(serial, issuer_id)

        FIELD_ORDER = 21888242871839275222246405745257275088548364400416034343698204186575808495617
        commitment = commitment % FIELD_ORDER


        mt = MerkleTree([commitment], depth=DEPTH)
        root = mt.get_root()
        path, path_indices = mt.get_proof(leaf_index)

    inputs = {
        "birth_year": birth_year,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "current_year": current_year,
        "current_month": current_month,
        "current_day": current_day,
        "nationality": nationality,
        "expiry_year": expiry_year,
        "expiry_month": expiry_month,
        "valid_signature": valid_signature,   
        "revealed_commitment": commitment,
        "merkle_root": root,
        "pathElements": path,  # keep them as integers, not strings
        "pathIndices": path_indices,
        "credential_serial_lo": serial,
        "issuer_id": issuer_id
    }
    
    write_json(input_json, inputs)

    # Generate witness
    print("[Witness] Generating witness...")
    subprocess.run([
        "node", f"{circom_folder}/{circuit_name}_js/generate_witness.js",
        wasm_path, input_json, witness_path
    ], check=True)
    

    # Generate proof
    print("[Proof] Creating PLONK proof...")
    subprocess.run([
        "snarkjs", "plonk", "prove",
        zkey_path, witness_path, proof_path, public_path
    ], check=True)

    return {
        "proof": proof_path,
        "public": public_path
    }

def verify_zk_proof():
    print("[ZK] snarkjs verify output:")
    subprocess.run(
        ["snarkjs", "plonk", "verify",
        "zk/verification_key.json",
        "out/public.json", "out/proof.json"],
        check=True
    )


import subprocess
import os
from utils import write_json

circom_folder = "zk"
circuit_name = "eligibility"
wasm_path = f"{circom_folder}/{circuit_name}_js/{circuit_name}.wasm"
input_json = f"{circom_folder}/input.json"
witness_path = f"{circom_folder}/witness.wtns"
zkey_path = f"{circom_folder}/{circuit_name}_final.zkey"
proof_path = "out/proof.json"
public_path = "out/public.json"

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

"""!!"""
def generate_zk_proof(birth_year, birth_month, birth_day, expiry_year, expiry_month, nationality,
    current_year, current_month, current_day, valid_signature
):
    inputs = {
        "birth_year": birth_year,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "expiry_year": expiry_year,
        "expiry_month": expiry_month,
        "nationality": nationality,
        "current_year": current_year,
        "current_month": current_month,
        "current_day": current_day,
        "valid_signature": valid_signature,
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
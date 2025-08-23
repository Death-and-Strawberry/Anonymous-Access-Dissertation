import base64, json, os, subprocess, tempfile, hashlib
from typing import List, Tuple

from ursa_bbs_signatures import (
    BbsKey, VerifyProofRequest, verify_proof as bbs_verify_proof
)

KEYS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keys"))

def load_merkle_root():
    """
    If keys/merkle_root.json exists, return (root_hex_lower, epoch_int), else None.
    """
    path = os.path.join(KEYS_DIR, "merkle_root.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return data["root_hex"].lower(), int(data["epoch"])

def verify_bbs_selective_disclosure(
    proof_b64: str,
    nonce_b64: str,
    message_count: int,
    revealed_ordered: List[Tuple[str, bytes]],
    bbs_public_key_bytes: bytes
) -> bool:
    """
    revealed_ordered: list of (name, bytes) in the EXACT signing order for revealed messages only.
    """
    proof = base64.b64decode(proof_b64)
    nonce = base64.b64decode(nonce_b64)
    revealed_vals = [b for _, b in revealed_ordered]

    bbs_key = BbsKey(bbs_public_key_bytes, message_count)
    req = VerifyProofRequest(
        proof=proof,
        public_key=bbs_key,
        messages=revealed_vals,
        nonce=nonce
    )
    return bbs_verify_proof(req)

def verify_plonk_with_snarkjs(vk_json_bytes: bytes, proof_json_b64: str, public_json_b64: str) -> bool:
    """
    snarkjs plonk verify <vk.json> <public.json> <proof.json>
    """
    proof_bytes = base64.b64decode(proof_json_b64)
    public_bytes = base64.b64decode(public_json_b64)

    with tempfile.TemporaryDirectory() as td:
        vk_path = os.path.join(td, "vk.json")
        proof_path = os.path.join(td, "proof.json")
        public_path = os.path.join(td, "public.json")

        with open(vk_path, "wb") as f:
            f.write(vk_json_bytes)
        with open(proof_path, "wb") as f:
            f.write(proof_bytes)
        with open(public_path, "wb") as f:
            f.write(public_bytes)

        result = subprocess.run(
            ["snarkjs", "plonk", "verify", vk_path, public_path, proof_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0

def load_vk_json_bytes() -> bytes:
    """
    Place your circuit’s verification key at: app/keys/verification_key.json
    """
    path = os.path.join(KEYS_DIR, "verification_key.json")
    with open(path, "rb") as f:
        return f.read()

def derive_pseudo_user_id(pk_bind_bytes: bytes, domain_tag: str = "therapy-platform") -> str:
    h = hashlib.blake2b(digest_size=32)
    h.update(domain_tag.encode())
    h.update(pk_bind_bytes)
    return h.hexdigest()

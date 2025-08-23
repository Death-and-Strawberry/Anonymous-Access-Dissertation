import hashlib
from bbs.sign import issue_credentials, verify_attributes
from bbs.create_bbs_proof import create_bbs_selective_proof
from zk.generate_proof import compile_circuit, generate_zk_proof, verify_zk_proof
from zk.trusted_setup import trusted_setup
from get_inputs import collect_user_inputs
import base64
from utils import write_json


attributes = collect_user_inputs()
revealed_fields = ["expiry_year","expiry_month", "pk_bind", "commitment"]

signature, keypair, tree, serial, issuer_id, all_keys, signing_key, pk_bind_bytes = issue_credentials(attributes)


is_signature_valid = verify_attributes(attributes, signature, keypair, tree, all_keys)
check_signature = 1 if is_signature_valid else 0

compile_circuit()
trusted_setup()

bbs_proof, revealed_attrs_bytes, bbs_pub, nonce, merkle_proof, serial, issuer_id, leaf_index = create_bbs_selective_proof(
    signature=signature,
    keypair=keypair,
    attributes=attributes,
    revealed_fields=revealed_fields,
    tree=tree,
    serial=serial,
    issuer_id=issuer_id,
    all_keys=all_keys,
    pk_bind_bytes=pk_bind_bytes
)

pathElements, pathIndices = merkle_proof


proof_files = generate_zk_proof(
    birth_year=attributes["birth_year"],
    birth_month=attributes["birth_month"],
    birth_day=attributes["birth_day"],
    expiry_year=attributes["expiry_year"],
    expiry_month=attributes["expiry_month"],
    nationality=attributes["nationality"],
    current_year=attributes["current_year"],
    current_month=attributes["current_month"],
    current_day=attributes["current_day"],
    valid_signature=check_signature,
    serial=serial,
    issuer_id=issuer_id,
    merkle_leaves=tree.leaves,
    leaf_index=leaf_index
)

print("Generated proof files:")
print(proof_files)


verify_zk_proof()



def b64(b): 
    return base64.b64encode(b).decode()

revealed_ordered = [
    {"name": "expiry_year",  "value": str(attributes["expiry_year"]), "encoding": "utf8"},
    {"name": "expiry_month", "value": str(attributes["expiry_month"]), "encoding": "utf8"},
    {"name": "pk_bind",      "value": b64(pk_bind_bytes),             "encoding": "base64"},
    {"name": "commitment",   "value": b64(revealed_attrs_bytes["commitment"]), "encoding": "base64"},
]


payload = {
    "bbs_public_key_b64": b64(bbs_pub),
    "bbs_proof": b64(bbs_proof),
    "bbs_nonce": b64(nonce),
    "message_count": len(attributes) + 2,
    "revealed": revealed_ordered,
    "plonk_proof": b64(open("out/proof.json","rb").read()),
    "plonk_public": b64(open("out/public.json","rb").read()),
    "merkle_root_hex": hex(tree.get_root())[2:],
    "epoch": 1
    }

input_payload = "out/input_payload.json"
write_json(path=input_payload, data=payload)


# Generate pseudo ID
pseudo_id = hashlib.sha256(pk_bind_bytes).hexdigest()[:16]

print(f"Pseudo ID: {pseudo_id}")
print("\nIMPORTANT: Keep your secret binding key safe!")
print("Use this key to sign authentication challenges in the login page.\n")
# Get the 64-byte Ed25519 private key (seed + public key)
full_sk = signing_key.encode()
print(base64.b64encode(full_sk).decode())


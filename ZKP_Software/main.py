from bbs.sign import issue_credentials, verify_attributes
from bbs.create_bbs_proof import create_bbs_selective_proof, verify_bbs_proof
from zk.generate_proof import compile_circuit, generate_zk_proof, verify_zk_proof
from zk.trusted_setup import trusted_setup
from get_inputs import collect_user_inputs



attributes = collect_user_inputs()
revealed_fields = ["expiry_year","expiry_month", "commitment"]

signature, keypair, tree, serial, issuer_id, all_keys = issue_credentials(attributes)

is_signature_valid = verify_attributes(attributes, signature, keypair, tree, all_keys)
check_signature = 1 if is_signature_valid else 0

compile_circuit()
trusted_setup()

bbs_proof, revealed_attrs_bytes, bbs_pub, nonce, merkle_proof, serial, issuer_id, leaf_index = create_bbs_selective_proof(
    signature=signature,
    keypair=keypair,
    attrs=attributes,
    revealed_fields=revealed_fields,
    tree=tree,
    serial=serial,
    issuer_id=issuer_id,
    all_keys=all_keys
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

bbs_validate = verify_bbs_proof(
    bbs_proof=bbs_proof,
    revealed_attrs=revealed_attrs_bytes,
    public_key=bbs_pub,
    nonce=nonce,
    message_count=len(attributes) + 1  # +1 for commitment
)


verify_zk_proof()


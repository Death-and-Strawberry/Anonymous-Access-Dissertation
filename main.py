from bbs.sign import issue_credentials, verify_attributes
from bbs.create_bbs_proof import create_bbs_selective_proof, verify_bbs_proof
from zk.generate_proof import compile_circuit, generate_zk_proof
from zk.trusted_setup import trusted_setup
from get_inputs import collect_user_inputs

def main():
    # Collect all user input
    attributes = collect_user_inputs()

    # Decide the field that will be used for selective disclosure
    revealead_fields = ["nationality"]

    # Generate BBS+ signature on attributes (Acts like a signing authority)
    signature, keypair = issue_credentials(attributes)

    # Verify BBS+ signature to get a boolean for zk circuit input
    is_signature_valid = verify_attributes(attributes, signature, keypair)
    if is_signature_valid == True:
        check_signature = 1
    else:
        check_signature = 0

    # Compile the circom circuit which generates the witness
    compile_circuit()

    # Generate files for universal setup
    trusted_setup()

    # Generate a proof for the selective disclosure scheme
    bbs_proof, revealed_attrs, bbs_pub, nonce = create_bbs_selective_proof(signature=signature, keypair=keypair,
                                                            attrs=attributes, revealed_fields=revealead_fields)
    
    # Generate Cirom proof
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
        valid_signature=check_signature
)
    
    print("Generated proof files:")
    print(proof_files)

    #Validate the proof generated.
    bbs_validate = verify_bbs_proof(bbs_proof=bbs_proof, revealed_attrs=revealed_attrs,
                                    public_key=bbs_pub, nonce=nonce, message_count=len(attributes))
    

main()
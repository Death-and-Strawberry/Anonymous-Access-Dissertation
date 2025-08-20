from ursa_bbs_signatures import BlsKeyPair, sign, SignRequest, verify, VerifyRequest, BbsKey
from merkle import poseidon_hash, MerkleTree, poseidon_hash_two, FIELD_ORDER
import os
from nacl import signing

def issue_credentials(attributes: dict, issuer_id: int = 42):
    """
    - attributess: dictionary of attributes (preserve insertion order or pass explicit ordering)
    - issuer_id: integer identifying the issuer
    Returns:
      signature, keypair, tree, serial (int), issuer_id (int), all_keys (list)
    """

    #Generate holder binding keypair for each credential (for replay attack resistance as proof is menat to made once and unlinkable)
    bind_signing_key = signing.SigningKey.generate()
    bind_verify_key = bind_signing_key.verify_key
    pk_bind_bytes = bytes(bind_verify_key)


    # deterministic ordering of attributes, as ordering inconsistencies cause issues
    all_keys = list(attributes.keys())

    # Holder secret serial (in a real system holder generates this and issuer signs commitment). 
    # For the sake of this, we use random to emulate this
    attempt = 0
    for attempt in range(3): #Safeguarding for the case that the serial produced is 0
        serial = int.from_bytes(os.urandom(32), "big")
        serial = serial % FIELD_ORDER #Because poseidon takes field elements mod p
        if serial > 0:
            break

    # Compute commitment C = Poseidon(serial, issuer_id)
    commitment = poseidon_hash_two(serial, issuer_id)

    # Build Merkle tree over commitments. As of now, only the one commitment, will emualate multiple users later
    tree = MerkleTree([commitment], depth=8)

    # Prepare messages (BBS+ expects bytes). Sign RAW attribute values (so revealed fields are human readable),
    # and append commitment_bytes as the final message at a fixed position.

    messages_bytes = []
    for k in all_keys:
        messages_bytes.append(str(attributes[k]).encode()) 

    #Add the pk_bind to the list of attributes
    messages_bytes.append(pk_bind_bytes)

    # commitment as 32-byte big-endian for BBS+
    commitment_bytes = commitment.to_bytes(32, "big")
    messages_bytes.append(commitment_bytes)

    # Sign all messages
    keypair = BlsKeyPair.generate_g2()
    request = SignRequest(messages=messages_bytes, key_pair=keypair)
    signature = sign(request)

    return signature, keypair, tree, serial, issuer_id, all_keys, bind_signing_key, pk_bind_bytes


def verify_attributes(attributes: dict, signature, keypair, tree: MerkleTree, all_keys):
    """
    Verify the full BBS+ signature over the raw attribute bytes + commitment (same ordering).
    """

    # same order used at signing
    messages_bytes = [str(attributes[k]).encode() for k in all_keys]

    # commitment taken from tree (assumes the tree contains the commitment at known position(s))
    #In this case will be the root as we only have one commitment
    commitment_int = tree.get_root()

    commitment_bytes = commitment_int.to_bytes(32, "big")
    messages_bytes.append(commitment_bytes)

    request = VerifyRequest(messages=messages_bytes, signature=signature, key_pair=keypair)
    
    return verify(request) 

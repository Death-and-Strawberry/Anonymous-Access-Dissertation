# bbs/create_bbs_proof.py
from ursa_bbs_signatures import (
    ProofMessage,
    ProofMessageType,
    CreateProofRequest,
    create_proof,
    BbsKey,
    verify_proof,
    VerifyProofRequest,
)
import os, ctypes
from bbs.ffi_bindings import lib, ByteBuffer, ExternError
from merkle import MerkleTree, poseidon_hash_two

def bls_to_bbs_key_via_ffi(bls_pub_bytes: bytes, message_count: int) -> bytes:
    """Custom method which calls the function bls_public_key_to_bbs_key
            which is not present in the python ffi_wrapper for ursa_bbs_signatures"""

    # Wrap the raw BLS public key bytes into a C-compatible ByteBuffer struct
    bls_buf = ByteBuffer(
        len=len(bls_pub_bytes),
        data=(ctypes.c_ubyte * len(bls_pub_bytes)).from_buffer_copy(bls_pub_bytes)
    )

    # Prepare an empty output buffer that the FFI call will fill with the new BBS key
    out_buf = ByteBuffer()

    # Prepare a struct to hold potential error info returned from the FFI
    err = ExternError()

    # Tell ctypes the argument and return types for the FFI function:
        # ByteBuffer = BLS pubkey input
        # uint32 = number of messages supported in the BBS key
        # Pointer to ByteBuffer: where to write the BBS key output
        # Pointer to ExternError: where to write error info
    lib.bls_public_key_to_bbs_key.argtypes = [
        ByteBuffer, ctypes.c_uint32,
        ctypes.POINTER(ByteBuffer), ctypes.POINTER(ExternError)
    ]
    lib.bls_public_key_to_bbs_key.restype = ctypes.c_int  # the C function returns an int status code

    # Call into the native library to convert the BLS public key into a BBS key
    res = lib.bls_public_key_to_bbs_key(
        bls_buf, message_count,
        ctypes.byref(out_buf), ctypes.byref(err)
    )

    # If the native function wrote an error into `err`, raise a Python exception
    if err.code != 0:
        raise Exception(f"FFI Error: {err.message.decode()}")

    # Copy the generated BBS key bytes from the C output buffer into a Python bytes object
    return bytes(bytearray(out_buf.data[:out_buf.len]))


def create_bbs_selective_proof(signature, keypair, attributess: dict, revealed_fields: list, tree: MerkleTree, serial: int, issuer_id: int, all_keys: list):
    """
    A function to create a proof of only selected values (selective disclosure) using the BBS+ library 
    that has been imported from ffi-bbs-signatures.

    - signature, keypair: from issuer
    - attributes: original attribute dictionary
    - revealed_fields: which attribute keys to reveal
    - tree: MerkleTree containing commitments
    - serial, issuer_id: holder secret + issuer id
    - all_keys: deterministic ordering used for signing
    Returns:
      bbs_proof, revealed_attrs_bytes (dict key->bytes), bbs_pub, nonce, merkle_proof (pathElements, pathIndices), serial, issuer_id, leaf_index
    """

    # Recompute commitment int
    commitment_int = poseidon_hash_two(serial, issuer_id)
    commitment_bytes = commitment_int.to_bytes(32, "big")

    # Build ProofMessage list in same message order as signing
    messages = []
    for k in all_keys:
        raw = str(attributess[k]).encode()
        mtype = ProofMessageType.Revealed if k in revealed_fields else ProofMessageType.HiddenProofSpecificBlinding
        messages.append(ProofMessage(raw, mtype))

    # append commitment as final message (same position used when signing)
    commit_type = ProofMessageType.Revealed if "commitment" in revealed_fields else ProofMessageType.HiddenProofSpecificBlinding
    messages.append(ProofMessage(commitment_bytes, commit_type))

    nonce = os.urandom(16)
    message_count = len(messages)

    # Convert BLS public key to BBS and create proof
    bbs_pub = bls_to_bbs_key_via_ffi(keypair.public_key, message_count)
    public_key = BbsKey(bbs_pub, message_count)

    request = CreateProofRequest(
        signature=signature,
        public_key=public_key,
        messages=messages,
        nonce=nonce
    )
    bbs_proof = create_proof(request)

    # Build revealed_attrs_bytes mapping
    revealed_attrs_bytes = {}
    for k in revealed_fields:
        if k == "commitment":
            revealed_attrs_bytes["commitment"] = commitment_bytes
        else:
            revealed_attrs_bytes[k] = str(attributess[k]).encode()

    # Find commitment leaf index in tree and produce merkle proof
    try:
        leaf_index = tree.leaves.index(commitment_int)
    except ValueError:
        raise Exception("Commitment not found in Merkle tree")

    pathElements, pathIndices = tree.get_proof(leaf_index)

    # return the merkle proof as integers (pathElements) and bit array (pathIndices)
    merkle_proof = (pathElements, pathIndices)

    return bbs_proof, revealed_attrs_bytes, bbs_pub, nonce, merkle_proof, serial, issuer_id, leaf_index


def verify_bbs_proof(bbs_proof, revealed_attrs: dict, public_key: bytes, nonce: bytes, message_count: int) -> bool:
    """
    Verify BBS+ selective disclosure proof.
    revealed_attrs values are expected to be bytes (exact bytes used when creating the proof).
    """

    # Accept bytes directly or encode strings
    messages = []
    for v in revealed_attrs.values():
        if isinstance(v, bytes):
            messages.append(v)
        else:
            messages.append(str(v).encode())

    bbs_key = BbsKey(public_key, message_count)
    request = VerifyProofRequest(
        proof=bbs_proof,
        public_key=bbs_key,
        messages=messages,
        nonce=nonce
    )
    return verify_proof(request)

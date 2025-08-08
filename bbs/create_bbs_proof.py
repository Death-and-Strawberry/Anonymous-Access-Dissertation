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

"""Takes BLS key and the number of messages, calls Rust FFI to produce a BBS+ public key needed for proof generation""" 
def bls_to_bbs_key_via_ffi(bls_pub_bytes: bytes, message_count: int) -> bytes:

    # Wrap input bytes into bytebuffer struct
    bls_buf = ByteBuffer(len=len(bls_pub_bytes),
                         data=(ctypes.c_ubyte * len(bls_pub_bytes)).from_buffer_copy(bls_pub_bytes))
    
    # Output buffer and error container
    out_buf = ByteBuffer()
    err = ExternError()

    # Informing ctypes about the argument and return type of the Rust function
    lib.bls_public_key_to_bbs_key.argtypes = [ByteBuffer, ctypes.c_uint32,
                                              ctypes.POINTER(ByteBuffer), ctypes.POINTER(ExternError)]
    lib.bls_public_key_to_bbs_key.restype = ctypes.c_int # Returning 0 here indicates a success

    res = lib.bls_public_key_to_bbs_key(bls_buf, message_count,
                                        ctypes.byref(out_buf), ctypes.byref(err))
    if err.code != 0:
        raise Exception(f"FFI Error: {err.message.decode()}")

    # Converting the output to python bytes object
    return bytes(bytearray(out_buf.data[:out_buf.len])) 

"""!"""
def create_bbs_selective_proof(signature, keypair, attrs, revealed_fields):
    
    messages = []

    # Going through the attributes and assigning if they will be selective disclosed or not
    for k, v in attrs.items():
        proof_type = (ProofMessageType.Revealed
                      if k in revealed_fields
                      else ProofMessageType.HiddenProofSpecificBlinding)
        messages.append(ProofMessage(str(v).encode(), proof_type))

    nonce = os.urandom(16)
    message_count = len(messages)

    # Converting the key
    bbs_pub = bls_to_bbs_key_via_ffi(keypair.public_key, message_count)
    public_key = BbsKey(bbs_pub, message_count)

    # Create a proof resuest with given parameters
    request = CreateProofRequest(
        signature=signature,
        public_key=public_key,
        messages=messages,
        nonce=nonce
    )
    # Generation of the proof
    bbs_proof = create_proof(request)
    revealed_attrs = {k: attrs[k] for k in revealed_fields}
    return bbs_proof, revealed_attrs, bbs_pub, nonce



def verify_bbs_proof(bbs_proof, revealed_attrs, public_key, nonce, message_count):
    messages = [str(v).encode() for v in revealed_attrs.values()]

    bbs_key = BbsKey(public_key, message_count)
    
    request = VerifyProofRequest(
        proof=bbs_proof,
        public_key=bbs_key,
        messages=messages,
        nonce=nonce

    )
    return verify_proof(request)

import ctypes
import os

#path to compiled shared library
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
LIB_PATH = os.path.abspath(os.path.join(BASE_DIR, "ffi-bbs-signatures/target/release/libbbs.dylib"))


print(f"Trying to load libbbs from: {LIB_PATH}")

lib = ctypes.CDLL(LIB_PATH)

# Matches structs in the Rust library
class ByteBuffer(ctypes.Structure):
    _fields_ = [
        ("len", ctypes.c_size_t),  # length of buffer
        ("data", ctypes.POINTER(ctypes.c_ubyte)),  # pointer to raw byte array
    ]

class ExternError(ctypes.Structure):
    _fields_ = [
        ("code", ctypes.c_int),  # 0 means success, non-zero is error
        ("message", ctypes.c_char_p),  # pointer to null-terminated error message
    ]

# Define the bls_public_key_to_bbs_key function
lib.bls_public_key_to_bbs_key.argtypes = [
    ByteBuffer,  # public key
    ctypes.c_int,  # message count
    ctypes.POINTER(ByteBuffer),  # out bbs key
    ctypes.POINTER(ExternError)  # out error
]
lib.bls_public_key_to_bbs_key.restype = ctypes.c_uint8  # returns a u8 (bool)


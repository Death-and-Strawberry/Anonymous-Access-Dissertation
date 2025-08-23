import ctypes
import os,sys

#path to compiled shared library

platform = sys.platform
dynamiclib = ""

if platform == "darwin":
    dynamiclib = "libbbs.dylib"
elif platform == "linux" or "linux2":
    dynamiclib += "libbbs.so"
elif platform == "win32" or "cygwin" or "msys":
    dynamiclib += "libbbs.dll"
else:
    print(f"""Please check the extension of your dynamic libraries based on your os:{platform} and append the
           value of {dynamiclib} to have the correct extension, alternatively please check within the ffi-bbs-signatures/target/release
            for the extension of the of the libbbs file.""")
    if dynamiclib == "":
        exit


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
LIB_PATH = os.path.abspath(os.path.join(BASE_DIR, f"ffi-bbs-signatures/target/release/{dynamiclib}"))

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


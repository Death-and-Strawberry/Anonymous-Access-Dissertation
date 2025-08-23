from ursa_bbs_signatures import BbsKey, VerifyProofRequest, verify_proof
import os
import sys
import ctypes
from ctypes import cdll

def get_library_path():
    """
    Get the path to the BBS library using relative paths.
    This will work for anyone who clones the repo with the same structure.
    """
    # Get the directory where this file (bbs_verify.py) is located
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate up to the project root, then to the ZKP_Software directory
    # From: /path/to/Anonymous-Access-Dissertation/Therapy_platform/app/bbs_verify.py
    # To:   /path/to/Anonymous-Access-Dissertation/ZKP_Software/ffi-bbs-signatures/target/release/
    
    # Go up two levels: app -> Therapy_platform -> Anonymous-Access-Dissertation
    project_root = os.path.dirname(os.path.dirname(current_file_dir))
    
    # Navigate to the library
    library_path = os.path.join(
        project_root,
        "ZKP_Software", 
        "ffi-bbs-signatures", 
        "target", 
        "release"
    )
    
    # Determine the correct library file based on the platform
    if sys.platform == "darwin":  
        lib_file = "libbbs.dylib"
    elif sys.platform == "linux":
        lib_file = "libbbs.so"
    elif sys.platform == "win32":
        lib_file = "libbbs.dll" 
    else:
        raise OSError(f"Unsupported platform: {sys.platform}")
    
    full_library_path = os.path.join(library_path, lib_file)
    
    return full_library_path

def load_bbs_library():
    """Load the BBS library with error handling."""
    try:
        library_path = get_library_path()
        
        if not os.path.exists(library_path):
            raise FileNotFoundError(f"BBS library not found at: {library_path}")
        
        print(f"Loading BBS library from: {library_path}")
        return cdll.LoadLibrary(library_path)
        
    except Exception as e:
        print(f"Failed to load BBS library: {e}")
        raise

# Load the library when this module is imported
try:
    bbs_lib = load_bbs_library()
    print("BBS library loaded successfully")
except Exception as e:
    print(f"Warning: Could not load BBS library: {e}")
    bbs_lib = None

def verify_bbs_proof(bbs_proof, revealed, bbs_pub, nonce, message_count):
    """
    Verify a BBS+ proof.
    
    Args:
        bbs_proof: The BBS+ proof bytes
        revealed: Dictionary of revealed attributes
        bbs_pub: BBS+ public key bytes
        nonce: Nonce bytes
        message_count: Number of messages
    
    Returns:
        bool: True if proof is valid, False otherwise
    """
    if bbs_lib is None:
        raise RuntimeError("BBS library not loaded. Cannot verify proof.")
    
    try:
        # Your actual verification logic here using bbs_lib
        # This is a placeholder - replace with your actual BBS verification calls
        print(f"Verifying proof with {message_count} messages")
        print(f"Revealed attributes: {list(revealed.keys())}")
        
        # Example of how you might call the library function:
        # result = bbs_lib.verify_proof(bbs_proof, revealed, bbs_pub, nonce, message_count)
        # return bool(result)
        
        # For now, return True as a placeholder
        return True
        
    except Exception as e:
        print(f"BBS proof verification failed: {e}")
        return False
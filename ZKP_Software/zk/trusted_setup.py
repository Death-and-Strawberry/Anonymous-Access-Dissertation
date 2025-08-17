import os
import subprocess

def trusted_setup():
    zkey_final = "zk/eligibility_final.zkey"
    verification_key = "zk/verification_key.json"
    
    if os.path.exists(zkey_final) and os.path.exists(verification_key):
        print("[Setup] Trusted setup already done.")
        return
    
    print("[Setup] Running trusted setup...")
    
    # Use power 14 ptau for bigger circuit
    ptau_file = "zk/pot14_final.ptau"
    
    if not os.path.exists(ptau_file):
        # Create ptau with power 14 (supports up to 2^14 = 16384 constraints)
        subprocess.run([
            "snarkjs", "powersoftau", "new", "bn128", "14", "zk/pot14_0000.ptau", "-v"
        ], check=True)
        
        subprocess.run([
            "snarkjs", "powersoftau", "contribute", "zk/pot14_0000.ptau", "zk/pot14_0001.ptau",
            "--name=First", "-v"
        ], check=True)
        
        subprocess.run([
            "snarkjs", "powersoftau", "prepare", "phase2", "zk/pot14_0001.ptau", ptau_file, "-v"
        ], check=True)
    
    # Generate the circuit-specific proving key
    subprocess.run([
        "snarkjs", "plonk", "setup", "zk/eligibility.r1cs", ptau_file, zkey_final
    ], check=True)
    
    # *** ADD THIS: Generate verification key from the proving key ***
    subprocess.run([
        "snarkjs", "zkey", "export", "verificationkey", zkey_final, verification_key
    ], check=True)
    
    print("[Setup] Trusted setup complete.")
    print(f"[Setup] Generated proving key: {zkey_final}")
    print(f"[Setup] Generated verification key: {verification_key}")
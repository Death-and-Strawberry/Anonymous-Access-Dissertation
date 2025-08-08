import os
import subprocess

"""!!"""
def trusted_setup():

    zkey_final = "zk/eligibility_final.zkey"
    if os.path.exists(zkey_final):
        print("[Setup] Trusted setup already done.")
        return

    print("[Setup] Running trusted setup...")

    ptau_file = "zk/pot12_final.ptau"
    if not os.path.exists(ptau_file):
        subprocess.run([
            "snarkjs", "powersoftau", "new", "bn128", "12", "zk/pot12_0000.ptau", "-v"
        ], check=True)
        subprocess.run([
            "snarkjs", "powersoftau", "contribute", "zk/pot12_0000.ptau", "zk/pot12_0001.ptau",
            "--name=First", "-v"
        ], check=True)
        subprocess.run([
            "snarkjs", "powersoftau", "prepare", "phase2", "zk/pot12_0001.ptau", ptau_file, "-v"
        ], check=True)

    subprocess.run([
        "snarkjs", "plonk", "setup", "zk/eligibility.r1cs", ptau_file, zkey_final
    ], check=True)

    print("[Setup] Trusted setup complete.")

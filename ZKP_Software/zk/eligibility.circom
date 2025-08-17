pragma circom 2.1.4;

include "../node_modules/circomlib/circuits/comparators.circom";
include "../node_modules/circomlib/circuits/poseidon.circom";
include "./merkle.circom";
include "./UserDOB.circom";



template EligibilityCheck() {
    signal input birth_year;
    signal input birth_month;
    signal input birth_day;

    signal input current_year;
    signal input current_month;
    signal input current_day;

    signal input nationality;  // e.g. encoded or hashed value (e.g., 826 for UK)
    signal input expiry_year;
    signal input expiry_month;

    signal input valid_signature;  // 1 if BBS+ proof is valid (verifier should verify BBS+ off-circuit)

    // revealed_commitment: public value revealed in the BBS+ selective disclosure proof
    // merkle_root: public Merkle root (current snapshot of valid credentials)
    // pathElements / pathIndices: private witness arrays giving Merkle inclusion path
    // credential_serial_lo / credential_serial_hi: private witness(s) for serial (packing as needed)
    // issuer_id: public or private (we use as public here to keep simple; could be a constant in-circuit)
    signal input revealed_commitment;   // public input: Poseidon(serial, issuer_id)
    signal input merkle_root;           // public input
    signal input pathElements[8];      // private witness (sibling nodes)
    signal input pathIndices[8];       // private witness (0/1 bits)
    signal input credential_serial_lo;  // private witness (pack serial into field(s) as needed)
    signal input issuer_id;             // public input (must match the issuer used when computing commitment)
    
    signal output pub_revealed_commitment <== revealed_commitment;
    signal output pub_merkle_root <== merkle_root;
    signal output pub_issuer_id <== issuer_id;
    signal output pub_valid_signature <== valid_signature;
    signal output pub_current_year <== current_year; 
    signal output pub_current_month <== current_month; 
    signal output pub_current_day <== current_day;
    signal output pub_expiry_year <== expiry_year; 
    signal output pub_expiry_month <== expiry_month;

    // Age check
    component isAdult = UserDOB();
    isAdult.birth_year <== birth_year;
    isAdult.birth_month <== birth_month;
    isAdult.birth_day <== birth_day;
    isAdult.current_year <== current_year;
    isAdult.current_month <== current_month;
    isAdult.current_day <== current_day;

    // Nationality check (e.g., UK == 826)
    component isCorrectNationality = IsEqual();
    isCorrectNationality.in[0] <== nationality;
    isCorrectNationality.in[1] <== 826;

    // Expiry check
    component year_gt = GreaterThan(12);
    year_gt.in[0] <== expiry_year;
    year_gt.in[1] <== current_year;

    component same_year = IsEqual();
    same_year.in[0] <== expiry_year;
    same_year.in[1] <== current_year;

    component month_geq = GreaterEqThan(6);
    month_geq.in[0] <== expiry_month;
    month_geq.in[1] <== current_month;

    // Combine: year_gt OR (same_year AND month_geq)
    signal month_ok_if_same_year;
    month_ok_if_same_year <== same_year.out * month_geq.out;

    signal expiry_logic;
    expiry_logic <== year_gt.out + month_ok_if_same_year;

    // Make expiry_logic equate to 0 or 1
    component expiry_cap = GreaterEqThan(2);
    expiry_cap.in[0] <== expiry_logic;
    expiry_cap.in[1] <== 1;

    signal notExpired;
    notExpired <== expiry_cap.out;

    // Compute commitment from serial and issuer_id inside circuit 
    // If the serial is larger than the field size you must pack/split it into multiple inputs
    // and adapt both Python and this circuit accordingly.
    component commitPose = Poseidon(2);
    commitPose.inputs[0] <== credential_serial_lo;
    commitPose.inputs[1] <== issuer_id;
    signal computed_commitment;
    computed_commitment <== commitPose.out;

    // equality check between computed_commitment and revealed_commitment (revealed in BBS+)
    component eqCommit = IsEqual();
    eqCommit.in[0] <== computed_commitment;
    eqCommit.in[1] <== revealed_commitment;

    // Merkle inclusion check
    component merkle = MerkleInclusion(8);
    merkle.leaf <== revealed_commitment;
    for (var i = 0; i < 8; i++) {
        merkle.pathElements[i] <== pathElements[i];
        merkle.pathIndices[i] <== pathIndices[i];
    }
    merkle.root <== merkle_root;

    signal inValidTree;
    inValidTree <== merkle.out;

    // Final eligibility = age OK AND nationality OK AND not expired AND BBS+ signature valid
    // AND computed commitment matches revealed commitment AND commitment is included in Merkle tree (not revoked)
    signal intermediate1;
    signal intermediate2;
    signal intermediate3;
    signal intermediate4;
    signal intermediate5;
    signal final_valid;

    intermediate1 <== isAdult.is_adult * isCorrectNationality.out;
    intermediate2 <== intermediate1 * notExpired;
    intermediate3 <== intermediate2 * valid_signature;
    intermediate4 <== intermediate3 * eqCommit.out;
    intermediate5 <== intermediate4 * inValidTree;

    final_valid <== intermediate5;

    signal output eligible <== final_valid;

}

// Instantiate
component main = EligibilityCheck();


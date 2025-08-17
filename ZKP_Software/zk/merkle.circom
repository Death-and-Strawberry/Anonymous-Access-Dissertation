pragma circom 2.1.4;

include "../node_modules/circomlib/circuits/poseidon.circom";
include "../node_modules/circomlib/circuits/comparators.circom"; // for IsEqual


template Mux() {
    signal input sel;
    signal input in0;
    signal input in1;
    signal output out;

    sel * (sel - 1) === 0; // enforce sel is bit
    out <== in0 + sel * (in1 - in0);
}

template MerkleInclusion(depth) {
    signal input leaf;
    signal input root;
    signal input pathElements[depth];
    signal input pathIndices[depth];

    component poseidonHash[depth];
    signal currentHash[depth + 1];

    // Declare arrays for mux components
    component leftMux[depth];
    component rightMux[depth];

    signal left[depth];
    signal right[depth];

    currentHash[0] <== leaf;

    for (var i = 0; i < depth; i++) {
        // create mux for left: if pathIndices[i]==0 -> currentHash[i], else pathElements[i]
        leftMux[i] = Mux();
        leftMux[i].sel <== pathIndices[i];
        leftMux[i].in0 <== currentHash[i];
        leftMux[i].in1 <== pathElements[i];
        left[i] <== leftMux[i].out;

        // create mux for right: if pathIndices[i]==0 -> pathElements[i], else currentHash[i]
        rightMux[i] = Mux();
        rightMux[i].sel <== pathIndices[i];
        rightMux[i].in0 <== pathElements[i];
        rightMux[i].in1 <== currentHash[i];
        right[i] <== rightMux[i].out;

        poseidonHash[i] = Poseidon(2);
        poseidonHash[i].inputs[0] <== left[i];
        poseidonHash[i].inputs[1] <== right[i];

        currentHash[i + 1] <== poseidonHash[i].out;
    }

    component isRootEqual = IsEqual();
    isRootEqual.in[0] <== currentHash[depth];
    isRootEqual.in[1] <== root;

    signal output out;
    out <== isRootEqual.out;
}

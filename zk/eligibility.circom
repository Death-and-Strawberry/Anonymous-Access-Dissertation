pragma circom 2.1.4;

include "../node_modules/circomlib/circuits/comparators.circom";
include "./UserDOB.circom";

template EligibilityCheck() {
    // Inputs
    signal input birth_year;
    signal input birth_month;
    signal input birth_day;

    signal input current_year;
    signal input current_month;
    signal input current_day;

    signal input nationality;  // e.g. encoded or hashed value (e.g., 826 for UK)
    signal input expiry_year;
    signal input expiry_month;

    signal input valid_signature;  // 1 if BBS+ proof is valid, else 0

    // Subcomponent: Age check
    component isAdult = UserDOB();
    isAdult.birth_year <== birth_year;
    isAdult.birth_month <== birth_month;
    isAdult.birth_day <== birth_day;
    isAdult.current_year <== current_year;
    isAdult.current_month <== current_month;
    isAdult.current_day <== current_day;

    // Subcomponent: Nationality check (e.g., UK == 826)
    component isCorrectNationality = IsEqual();
    isCorrectNationality.in[0] <== nationality;
    isCorrectNationality.in[1] <== 826;

    // Expiry check:
    // Valid if: expiry_year > current_year
    // OR (expiry_year == current_year AND expiry_month >= current_month)

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

    // Clamp expiry_logic to 0 or 1
    component expiry_cap = GreaterEqThan(2);
    expiry_cap.in[0] <== expiry_logic;
    expiry_cap.in[1] <== 1;

    signal notExpired;
    notExpired <== expiry_cap.out;

    // Final eligibility = age OK AND nationality OK AND not expired
    signal intermediate;
    signal intermediate2;
    signal output valid;

    intermediate <== isAdult.is_adult * isCorrectNationality.out;
    intermediate2 <== intermediate * notExpired;
    valid <== intermediate2 * valid_signature;
}

// Instantiate
component main = EligibilityCheck();

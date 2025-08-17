pragma circom 2.1.4;

include "../node_modules/circomlib/circuits/comparators.circom";

template UserDOB() {
    signal input birth_year;
    signal input birth_month;
    signal input birth_day;

    signal input current_year;
    signal input current_month;
    signal input current_day;

    signal output is_adult;

    // Initial Estimate of age
    signal age_years;
    age_years <== current_year - birth_year;

    // Check if birthday has passed this year
    component month_gt = GreaterThan(6);
    month_gt.in[0] <== current_month;
    month_gt.in[1] <== birth_month;

    // If months are the same, compare the day
    component day_geq = GreaterEqThan(6);
    day_geq.in[0] <== current_day;
    day_geq.in[1] <== birth_day;

    component same_month = IsEqual();
    same_month.in[0] <== current_month;
    same_month.in[1] <== birth_month;

    // Check if the birthday has passed, when month is greater or if the month is the same but the day is greater than or equal)
    signal same_month_and_day;
    same_month_and_day <== same_month.out * day_geq.out;

    signal birthday_logic;
    birthday_logic <== month_gt.out + same_month_and_day;

    component birthday_cap = GreaterEqThan(2);
    birthday_cap.in[0] <== birthday_logic;
    birthday_cap.in[1] <== 1;

    signal birthday_passed;
    birthday_passed <== birthday_cap.out;

    // full_age = age_years - (1 - birthday_passed)
    signal full_age;
    full_age <== age_years - (1 - birthday_passed);

    // is_adult = full_age >= 18
    component adult_check = GreaterEqThan(6);
    adult_check.in[0] <== full_age;
    adult_check.in[1] <== 18;

    is_adult <== adult_check.out;
}

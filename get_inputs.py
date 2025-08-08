# get_inputs.py
from datetime import datetime

NATIONALITY_CODES = {
    "UK": 826,
    "USA": 840,
    "FR": 250,
    "DE": 276,
    "ES": 724,
    "IT": 380,
}

countries = ""
for k,v in NATIONALITY_CODES.items():
    countries += k + "\n"

# Get current date
now = datetime.now()
current_year = now.year
current_month = now.month
current_day = now.day

# Obtain Nationality code from string.
def get_nationality_code(max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        try:
            nationality_str = input("Enter your nationality (UK, USA, FR, etc): ").strip().upper()
            if nationality_str in NATIONALITY_CODES:
                return NATIONALITY_CODES[nationality_str]
            else:
                print(f"Please select a supported nationality: \n{countries}Try again.")
        except ValueError:
            pass  # still counts as an attempt
        attempts += 1
    raise ValueError("Too many invalid attempts for input: Enter your nationality (UK, USA, FR, etc): ")


#Ensure correct date (e.g. account for leap years, 28 days of Feb etc)
def validate_date(year, month, day):
    try:
        datetime(year, month, day)
        return True
    except ValueError:
        return False

def get_int_input(prompt, min_value, max_value, max_attempts = 5):
    attempts = 0
    while attempts < max_attempts:
        try:
            value = int(input(prompt).strip())
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        attempts += 1
    raise ValueError(f"Too many invalid attempts for input: {prompt}")

def collect_user_inputs(predefined_inputs=None):

    # For allowing predefined test inputs.
    if predefined_inputs:
        return predefined_inputs 
    else:

        print("=== Enter your ID details ===")

        # Full date of birth
        birth_year = get_int_input("Birth year (e.g. 2003): ", 1900, datetime.now().year)
        birth_month = get_int_input("Birth month (1–12): ", 1, 12)

        while True:
            birth_day = get_int_input("Birth day (1–31): ", 1, 31)
            if validate_date(birth_year, birth_month, birth_day):
                break
            print("Invalid birth date. Please enter a valid day for the given month and year.")


        # Expiry year and month
        expiry_year = get_int_input("Document expiry year (e.g. 2030): ", datetime.now().year, 2100)
        while True:
            expiry_month = get_int_input("Document expiry month (1–12): ", 1, 12)
            if expiry_year == current_year and expiry_month < current_month:
                print("Expiry month cannot be before the current month in the current year.")
            else:
                break

        nationality = get_nationality_code()


        return {
            "birth_year": birth_year,
            "birth_month": birth_month,
            "birth_day": birth_day,
            "expiry_year": expiry_year,
            "expiry_month": expiry_month,
            "nationality": nationality,
            "current_year": current_year,
            "current_month": current_month,
            "current_day": current_day,
        }

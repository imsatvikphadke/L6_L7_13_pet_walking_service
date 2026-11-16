import math

# ---------------------------------------------------------------------------
# Hardened version of processor.py (Lab 7 - Fuzzing for Input Validation Bugs)
#
# Design: every function validates its input and NEVER raises on bad data.
#   * parse_walk_schedule         -> returns an "Error: ..." string on bad input
#   * compute_pace_per_pet        -> returns None on bad input
#   * lookup_temperament_surcharge-> returns None on bad input
# ---------------------------------------------------------------------------

MAX_PETS = 20          # sanity limits so absurd values are rejected
MAX_MINUTES = 24 * 60

WEEKEND_FEES = {"YES": 15.0, "NO": 0.0}

TEMPERAMENT_SURCHARGES = {
    "CAL": 0.0, "CALM": 0.0,
    "PLY": 5.0, "PLAYFUL": 5.0,
    "REA": 12.0, "REACTIVE": 12.0,
    "AGG": 20.0, "AGGRESSIVE": 20.0,
}


def parse_walk_schedule(schedule_spec):
    """Parse 'pets-mins-weekend' (e.g. '2-30-YES') and return a price summary.

    Returns an 'Error: ...' string if the input is invalid.
    """
    if not isinstance(schedule_spec, str):
        return "Error: schedule must be a string"

    parts = schedule_spec.strip().split('-')
    if len(parts) != 3:
        return "Error: expected format pets-mins-weekend (e.g. 2-30-YES)"

    pets_str, mins_str, weekend_str = (p.strip() for p in parts)

    try:
        pets = int(pets_str)
        mins = int(mins_str)
    except (ValueError, OverflowError):
        return "Error: pets and mins must be whole numbers"

    if not 1 <= pets <= MAX_PETS:
        return f"Error: pets must be between 1 and {MAX_PETS}"
    if not 1 <= mins <= MAX_MINUTES:
        return f"Error: mins must be between 1 and {MAX_MINUTES}"

    weekend_key = weekend_str.upper()
    if weekend_key not in WEEKEND_FEES:
        return "Error: weekend flag must be YES or NO"
    weekend_fee = WEEKEND_FEES[weekend_key]

    base_fee = 20.0 if mins <= 30 else 35.0
    total = base_fee + (pets * 5.0) + weekend_fee
    return f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"


def compute_pace_per_pet(walk_metrics_str):
    """Parse 'mins/pets' (e.g. '45/3') and return minutes per pet (float).

    Returns None if the input is invalid.
    """
    if not isinstance(walk_metrics_str, str):
        return None

    parts = walk_metrics_str.split('/')
    if len(parts) != 2:
        return None

    try:
        mins = float(parts[0])
        pets = float(parts[1])
    except (ValueError, OverflowError):
        return None

    # reject nan / inf, negatives and zero pets (division by zero)
    if not (math.isfinite(mins) and math.isfinite(pets)):
        return None
    if mins < 0 or pets <= 0:
        return None

    try:
        pace = mins / pets
    except (ZeroDivisionError, OverflowError):
        return None
    if not math.isfinite(pace):      # e.g. 1e308 / 1e-308 overflows to inf
        return None
    return round(pace, 2)


def lookup_temperament_surcharge(temperament_code):
    """Return the surcharge for a temperament code/name (e.g. 'CALM', 'AGG').

    Returns None if the code is not recognised.
    """
    if not isinstance(temperament_code, str):
        return None
    return TEMPERAMENT_SURCHARGES.get(temperament_code.strip().upper())


def main():
    print("==== Running parse_walk_schedule ====")
    s_input = input("Enter schedule (e.g. 2-30-YES): ")
    print(parse_walk_schedule(s_input))

    print("\n==== Running compute_pace_per_pet ====")
    p_input = input("Enter minutes/pets (e.g. 45/3): ")
    result = compute_pace_per_pet(p_input)
    print("Pace (min/pet):", result if result is not None else "Error: invalid input")

    print("\n==== Running lookup_temperament_surcharge ====")
    t_input = input("Enter temperament code (e.g. CALM, PLAYFUL, AGGRESSIVE): ")
    surcharge = lookup_temperament_surcharge(t_input)
    if surcharge is None:
        print("Surcharge: Error: unknown temperament code")
    else:
        print("Surcharge: $", surcharge)


if __name__ == "__main__":
    main()

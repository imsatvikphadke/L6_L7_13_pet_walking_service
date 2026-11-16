from hypothesis import given, strategies as st
from processor import parse_walk_schedule, compute_pace_per_pet, lookup_temperament_surcharge


# ---------------------------------------------------------------------------
# 1. "No crash" tests - completed from the starter code (try / except)
# ---------------------------------------------------------------------------

@given(st.text() | st.none())
def test_parse_walk_schedule_no_crash(s):
    try:
        parse_walk_schedule(s)
    except Exception as e:
        assert False, f"parse_walk_schedule crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_compute_pace_per_pet_safe(s):
    try:
        compute_pace_per_pet(s)
    except Exception as e:
        assert False, f"compute_pace_per_pet crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_lookup_temperament_surcharge_safe(s):
    try:
        lookup_temperament_surcharge(s)
    except Exception as e:
        assert False, f"lookup_temperament_surcharge crashed with: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# 2. Extra property tests - more edge cases (non-string types, structured input)
# ---------------------------------------------------------------------------

anything = st.one_of(st.none(), st.integers(), st.floats(), st.booleans(),
                     st.binary(), st.lists(st.integers()), st.text())


@given(anything)
def test_all_functions_survive_any_type(x):
    for fn in (parse_walk_schedule, compute_pace_per_pet, lookup_temperament_surcharge):
        try:
            fn(x)
        except Exception as e:
            assert False, f"{fn.__name__} crashed on {x!r} with: {type(e).__name__}: {e}"


@given(st.integers(-10**6, 10**6), st.integers(-10**6, 10**6),
       st.text(max_size=8))
def test_parse_walk_schedule_structured(pets, mins, flag):
    out = parse_walk_schedule(f"{pets}-{mins}-{flag}")
    assert isinstance(out, str)
    assert out.startswith("Walk:") or out.startswith("Error:")


@given(st.integers(1, 20), st.integers(1, 1440), st.sampled_from(["YES", "NO", "yes", " No "]))
def test_parse_walk_schedule_valid_input_priced(pets, mins, flag):
    out = parse_walk_schedule(f"{pets}-{mins}-{flag}")
    assert out.startswith("Walk:")
    total = float(out.split("$")[1])
    assert total >= 25.0          # base 20 + at least one pet (5)


@given(st.floats(allow_nan=True, allow_infinity=True),
       st.floats(allow_nan=True, allow_infinity=True))
def test_compute_pace_per_pet_floats(mins, pets):
    result = compute_pace_per_pet(f"{mins}/{pets}")
    assert result is None or (isinstance(result, float) and result >= 0)


@given(st.floats(0, 1e6), st.floats(0.01, 1e3))
def test_compute_pace_per_pet_valid(mins, pets):
    assert compute_pace_per_pet(f"{mins}/{pets}") is not None


def test_compute_pace_per_pet_zero_pets():
    assert compute_pace_per_pet("45/0") is None


@given(st.text())
def test_lookup_temperament_surcharge_result_type(s):
    result = lookup_temperament_surcharge(s)
    assert result is None or result in (0.0, 5.0, 12.0, 20.0)


def test_lookup_temperament_surcharge_known_values():
    assert lookup_temperament_surcharge("CALM") == 0.0
    assert lookup_temperament_surcharge(" playful ") == 5.0
    assert lookup_temperament_surcharge("REA") == 12.0
    assert lookup_temperament_surcharge("AGGRESSIVE") == 20.0
    assert lookup_temperament_surcharge("CALAMITY") is None   # prefix-match bug

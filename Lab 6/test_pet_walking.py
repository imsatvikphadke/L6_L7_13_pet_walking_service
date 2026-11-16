
import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars


def test_single_standard_30_walk():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_30",
            "is_weekend": False,
            "walks": [{"num_pets": 1, "aggression_alert": False, "needs_meds": False}]
        }
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 27.0
    assert result["status"] == "COMPLETED"


def test_invalid_routes():
    with pytest.raises(ValueError):
        process_walking_routes("invalid", 5.0)


def test_negative_transport_fee():
    with pytest.raises(ValueError):
        process_walking_routes([], -1.0)


def test_unconfirmed_route():
    result = process_walking_routes(
        [{"route_confirmed": False}], 5.0
    )
    assert result == {
        "total_revenue": 0.0,
        "status": "ZERO_EARNINGS"
    }


@pytest.mark.parametrize(
    "session, expected",
    [
        ("standard_30", 27.0),
        ("standard_60", 40.0),
        ("express_15", 19.0),
    ],
)
def test_session_types(session, expected):
    routes = [{
        "route_confirmed": True,
        "session_type": session,
        "walks": [{"num_pets": 1}],
    }]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == expected


def test_unknown_session_type():
    result = process_walking_routes(
        [{
            "route_confirmed": True,
            "session_type": "unknown",
            "walks": [],
        }],
        5.0,
    )
    assert result["status"] == "ZERO_EARNINGS"


def test_zero_pets():
    result = process_walking_routes(
        [{
            "route_confirmed": True,
            "walks": [{"num_pets": 0}],
        }],
        5.0,
    )
    assert result["status"] == "ZERO_EARNINGS"


def test_large_pet_count():
    result = process_walking_routes(
        [{
            "route_confirmed": True,
            "session_type": "standard_30",
            "walks": [{"num_pets": 4}],
        }],
        5.0,
    )
    assert result["total_revenue"] == 48.6


def test_medication_fee():
    result = process_walking_routes(
        [{
            "route_confirmed": True,
            "session_type": "standard_30",
            "walks": [{
                "num_pets": 1,
                "needs_meds": True,
            }],
        }],
        5.0,
    )
    assert result["total_revenue"] == 33.0


def test_weekend_transport_fee():
    result = process_walking_routes(
        [{
            "route_confirmed": True,
            "session_type": "standard_30",
            "is_weekend": True,
            "walks": [{"num_pets": 1}],
        }],
        5.0,
    )
    assert result["total_revenue"] == 32.0


def test_aggression_alert():
    result = process_walking_routes(
        [{
            "route_confirmed": True,
            "session_type": "standard_30",
            "walks": [{
                "num_pets": 1,
                "aggression_alert": True,
            }],
        }],
        5.0,
    )
    assert result["status"] == "ZERO_EARNINGS"


def test_aggression_alert_for_60_minute_walk():
    result = process_walking_routes(
        [{
            "route_confirmed": True,
            "session_type": "standard_60",
            "walks": [
                {"num_pets": 1},
                {"num_pets": 1, "aggression_alert": True},
            ],
        }],
        5.0,
    )
    assert result["total_revenue"] == 0.0


def test_incident_audit():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "unknown",
            "walks": [],
        }
        for _ in range(5)
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "INCIDENT_AUDIT"


def test_empty_gps_data():
    assert inspect_gps_collars([]) == "NO_DATA"


def test_consecutive_weak_gps_signals():
    assert inspect_gps_collars([[15, 10]]) == "LOST_SIGNAL_ALERT"


def test_nonconsecutive_weak_gps_signals():
    assert inspect_gps_collars([[15, 30, 10]]) == "ONLINE"


def test_gps_signal_recovers():
    assert inspect_gps_collars([[10, 30, 25]]) == "ONLINE"

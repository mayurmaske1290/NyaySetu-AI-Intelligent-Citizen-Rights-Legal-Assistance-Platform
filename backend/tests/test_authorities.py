from app.authorities.demo_provider import haversine_km
from app.services.escalation import nearby


def test_distance_zero():
    assert haversine_km(19.07, 72.87, 19.07, 72.87) == 0


def test_bribe_escalation_prefers_anti_corruption():
    res = nearby(19.07, 72.87, "BRIBE_DEMAND")
    types = [a.type for a in res.most_appropriate]
    assert "ANTI_CORRUPTION" in types
    assert res.nearest
    assert "not always" in res.distinction.lower()

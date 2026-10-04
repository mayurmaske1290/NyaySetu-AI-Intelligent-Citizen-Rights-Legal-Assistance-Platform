from typing import List, Optional

from app.authorities.demo_provider import DEMO_AUTHORITIES, haversine_km
from app.schemas.analysis import Category
from app.schemas.authority import Authority, NearbyAuthoritiesResponse


TYPE_FOR_CATEGORY = {
    Category.TRAFFIC_STOP: ["TRAFFIC", "POLICE", "LEGAL_AID"],
    Category.BRIBE_DEMAND: ["ANTI_CORRUPTION", "LEGAL_AID", "POLICE"],
    Category.SCAM: ["OTHER", "CONSUMER", "POLICE", "LEGAL_AID"],
    Category.THREAT_HARASSMENT: ["POLICE", "LEGAL_AID"],
    Category.LEGAL_NOTICE: ["LEGAL_AID"],
    Category.OTHER: ["LEGAL_AID", "OTHER"],
}


def nearby(
    lat: Optional[float],
    lng: Optional[float],
    category: Optional[str],
) -> NearbyAuthoritiesResponse:
    items = [a.model_copy() for a in DEMO_AUTHORITIES]
    if lat is not None and lng is not None:
        for a in items:
            a.distance_km = round(haversine_km(lat, lng, a.latitude, a.longitude), 2)
        nearest = sorted(items, key=lambda x: x.distance_km or 9999)[:5]
    else:
        nearest = items[:5]

    preferred_types = TYPE_FOR_CATEGORY.get(category or "", ["LEGAL_AID"])
    appropriate: List[Authority] = []
    for t in preferred_types:
        for a in items:
            if a.type == t and a.authority_id not in {x.authority_id for x in appropriate}:
                appropriate.append(a)
        if len(appropriate) >= 4:
            break
    if not appropriate:
        appropriate = nearest[:3]

    return NearbyAuthoritiesResponse(
        nearest=nearest,
        most_appropriate=appropriate,
        demo_mode=True,
    )

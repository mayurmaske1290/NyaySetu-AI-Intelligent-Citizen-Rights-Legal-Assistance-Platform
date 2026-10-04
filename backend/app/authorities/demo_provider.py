import math
from typing import List

from app.schemas.authority import Authority

# Clearly labeled DEMO DATA. Do not treat phones/URLs as verified official contacts.
DEMO_AUTHORITIES: List[Authority] = [
    Authority(
        authority_id="demo-legal-aid-mumbai",
        name="[DEMO DATA] Legal aid desk — Mumbai (sample)",
        type="LEGAL_AID",
        city="Mumbai",
        state="Maharashtra",
        latitude=19.0760,
        longitude=72.8777,
        phone=None,
        website="https://nalsa.gov.in/",
        complaint_url=None,
        description="Demo pin near Mumbai. Replace with a verified local legal-aid office. NALSA website is a real official starting point; this pin is not a real office address.",
        is_demo=True,
    ),
    Authority(
        authority_id="demo-traffic-mumbai",
        name="[DEMO DATA] Traffic help sample — Mumbai",
        type="TRAFFIC",
        city="Mumbai",
        state="Maharashtra",
        latitude=19.0596,
        longitude=72.8295,
        phone=None,
        website=None,
        complaint_url=None,
        description="Demo only. Do not treat this as a real traffic police station.",
        is_demo=True,
    ),
    Authority(
        authority_id="demo-police-delhi",
        name="[DEMO DATA] Police sample pin — Delhi",
        type="POLICE",
        city="New Delhi",
        state="Delhi",
        latitude=28.6139,
        longitude=77.2090,
        phone=None,
        website=None,
        complaint_url=None,
        description="Demo pin. Emergency numbers must come from official local sources, not this list.",
        is_demo=True,
    ),
    Authority(
        authority_id="demo-consumer-pune",
        name="[DEMO DATA] Consumer forum sample — Pune",
        type="CONSUMER",
        city="Pune",
        state="Maharashtra",
        latitude=18.5204,
        longitude=73.8567,
        phone=None,
        website="https://ncdrc.nic.in/",
        complaint_url=None,
        description="Demo pin. National consumer dispute website is a real portal; this map pin is sample placement only.",
        is_demo=True,
    ),
    Authority(
        authority_id="demo-labour-delhi",
        name="[DEMO DATA] Labour help sample — Delhi",
        type="LABOUR",
        city="New Delhi",
        state="Delhi",
        latitude=28.6304,
        longitude=77.2177,
        phone=None,
        website="https://labour.gov.in/",
        complaint_url=None,
        description="Demo pin. Ministry site is real; this coordinate is not a verified office.",
        is_demo=True,
    ),
    Authority(
        authority_id="demo-cvc",
        name="[DEMO DATA] Anti-corruption complaint channel (portal pointer)",
        type="ANTI_CORRUPTION",
        city="New Delhi",
        state="Delhi",
        latitude=28.6271,
        longitude=77.2166,
        phone=None,
        website="https://cvc.gov.in/",
        complaint_url="https://cvc.gov.in/",
        description="Pointer to a known official anti-corruption body website. Map pin is DEMO placement, not a walk-in instruction.",
        is_demo=True,
    ),
    Authority(
        authority_id="demo-cyber",
        name="[DEMO DATA] National cybercrime reporting pointer",
        type="OTHER",
        city="New Delhi",
        state="Delhi",
        latitude=28.5275,
        longitude=77.2100,
        phone=None,
        website="https://www.cybercrime.gov.in/",
        complaint_url="https://www.cybercrime.gov.in/",
        description="Official national cybercrime reporting portal. Coordinates are DEMO only.",
        is_demo=True,
    ),
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

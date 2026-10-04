from typing import List, Optional

from pydantic import BaseModel


class Authority(BaseModel):
    authority_id: str
    name: str
    type: str
    city: str
    state: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    website: Optional[str] = None
    complaint_url: Optional[str] = None
    description: str
    is_demo: bool = True
    distance_km: Optional[float] = None


class NearbyAuthoritiesResponse(BaseModel):
    nearest: List[Authority]
    most_appropriate: List[Authority]
    distinction: str = (
        "Nearest physical location is not always the most appropriate complaint channel."
    )
    demo_mode: bool = True

from app.services.severity import fuse_severity
from app.schemas.analysis import Category, Severity


def test_bribe_is_high():
    assert fuse_severity([Category.TRAFFIC_STOP, Category.BRIBE_DEMAND], "asked for 500") == Severity.HIGH


def test_traffic_medium():
    assert fuse_severity([Category.TRAFFIC_STOP], "challan for helmet") == Severity.MEDIUM

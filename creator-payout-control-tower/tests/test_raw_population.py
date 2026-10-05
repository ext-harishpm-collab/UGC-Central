from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.raw_population_service import classify_content


def test_unknown_content_is_not_forced_to_novel():
    assert classify_content(None, None, None, "", "", "", "") == "UNCLASSIFIED"


def test_explicit_content_classification():
    assert classify_content(None, None, None, "Series", "", "", "") == "SERIES"
    assert classify_content(None, None, None, "Novel", "", "", "") == "NOVEL"
    assert classify_content(None, None, None, "N2A/A2A", "", "", "") == "N2A/A2A"

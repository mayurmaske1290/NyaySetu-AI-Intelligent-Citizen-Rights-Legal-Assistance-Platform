def test_traffic_bribe_fusion(client):
    r = client.post(
        "/api/analyze/text",
        json={
            "text": "Traffic police stopped me and asked me for ₹500 instead of giving a proper receipt.",
            "language": "en",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["primary_category"] == "TRAFFIC_STOP"
    assert "BRIBE_DEMAND" in body["secondary_categories"]
    assert body["severity"] == "HIGH"
    assert body["confidence_label"] in {"WELL_ESTABLISHED", "VERIFY_WITH_SOURCE", "UNCERTAIN"}
    assert body["what_not_to_do"]
    assert body["action_steps"]
    assert body["demo_mode"] is True
    assert "not legal advice" in body["disclaimer"].lower()


def test_scam_voice(client):
    r = client.post(
        "/api/analyze/voice-text",
        json={"transcript": "Someone asked for my UPI OTP saying my account will be blocked.", "language": "en"},
    )
    assert r.status_code == 200
    assert r.json()["primary_category"] == "SCAM"


def test_empty_rejected(client):
    r = client.post("/api/analyze/text", json={"text": "  ", "language": "en"})
    assert r.status_code == 400

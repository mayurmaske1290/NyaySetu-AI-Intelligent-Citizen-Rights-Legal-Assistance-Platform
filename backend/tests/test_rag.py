def test_rag_search(client):
    r = client.post("/api/rag/search", json={"query": "UPI OTP scam", "k": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["demo_mode"] is True
    assert body["results"]
    assert body["results"][0]["is_demo"] is True


def test_legal_sources(client):
    r = client.get("/api/legal/sources")
    assert r.status_code == 200
    assert r.json()["sources"]


def test_action_safety_transfer(client):
    r = client.post("/api/action-safety/check", json={"planned_action": "Should I transfer the money?"})
    assert r.status_code == 200
    assert "Pause" in r.json()["safer_step"]


def test_timeline_does_not_invent_clock(client):
    r = client.post(
        "/api/timeline/generate",
        json={"description": "They asked for documents then for payment.", "evidence": []},
    )
    assert r.status_code == 200
    events = r.json()["events"]
    assert all(e["inferred"] or e["event_time"] for e in events) or events
    assert all(e["event_time"] is None or e["event_time"] for e in events)

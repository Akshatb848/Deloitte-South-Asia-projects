"""API smoke tests with the LLM unavailable (retrieval-only fallback)."""
import shutil
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch):
    import main

    # Fresh index per test so the fake/real embedder is always used to build it.
    monkeypatch.setattr(main.rag_system, "vector_db_path", tempfile.mkdtemp(prefix="vdb_"))
    with TestClient(main.app) as c:
        yield c
    shutil.rmtree(main.rag_system.vector_db_path, ignore_errors=True)


def test_health_reports_rag_ready_and_llm_down(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["rag_initialized"] is True
    assert data["llm_connected"] is False
    assert data["status"] == "degraded"


def test_newsletter_months(client):
    months = client.get("/api/newsletter/months").json()["months"]
    assert months[0] == "April_2025"
    assert len(months) == 10


def test_newsletter_month_detail_and_404(client):
    res = client.get("/api/newsletter/June_2025")
    assert res.status_code == 200
    assert res.json()["month"] == "June 2025"
    assert client.get("/api/newsletter/March_1999").status_code == 404


def test_search_returns_relevant_chunk(client):
    res = client.post("/api/search", params={"query": "Kerala attendance APAAR coverage", "top_k": 3})
    assert res.status_code == 200
    results = res.json()["results"]
    assert results
    assert results[0]["type"] == "state_performance"


def test_chat_falls_back_to_retrieval_when_llm_down(client):
    res = client.post("/api/chat", json={"query": "smart classrooms and computer labs", "current_month": "April_2025"})
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "retrieval_only"
    assert "retrieval only" in data["response"]
    assert data["sources"]
    assert all(s["month"] == "April 2025" for s in data["sources"])
    assert "Smart Classrooms" in data["response"]


def test_state_comparison_uses_structured_data(client):
    res = client.post(
        "/api/compare",
        json={"entities": ["Kerala", "Gujarat"], "metric": "attendance", "months": ["April_2025"]},
    )
    assert res.status_code == 200
    text = res.json()["comparison_data"]["response"]
    assert "Kerala" in text and "Gujarat" in text

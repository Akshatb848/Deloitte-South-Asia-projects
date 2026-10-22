"""Retrieval tests on the bundled sample newsletter data."""
import asyncio

import pytest

from rag.rag_system import RAGSystem


def _build(tmp_path, monkeypatch):
    monkeypatch.setenv("VECTOR_DB_PATH", str(tmp_path / "vdb"))
    rag = RAGSystem()
    asyncio.run(rag.initialize())
    return rag


def test_chunks_cover_every_month_and_type(tmp_path, monkeypatch):
    rag = _build(tmp_path, monkeypatch)
    months = {d["month"] for d in rag.documents}
    types = {d["type"] for d in rag.documents}
    assert months == set(rag.get_available_months())
    assert {"overview", "highlight", "event", "state_performance", "infrastructure"} <= types


def test_month_filter_is_respected(tmp_path, monkeypatch):
    rag = _build(tmp_path, monkeypatch)
    results = asyncio.run(rag.search("attendance rate", top_k=3, filter_month="October_2025"))
    assert results
    assert all(r["month"] == "October_2025" for r in results)


def test_index_is_persisted_and_reloaded(tmp_path, monkeypatch):
    rag = _build(tmp_path, monkeypatch)
    assert (tmp_path / "vdb" / "index.faiss").exists()
    reloaded = _build(tmp_path, monkeypatch)
    assert len(reloaded.documents) == len(rag.documents)


@pytest.mark.real_model
def test_semantic_search_with_real_model(tmp_path, monkeypatch):
    rag = _build(tmp_path, monkeypatch)
    results = asyncio.run(rag.search("How many smart classrooms and computer labs were there?", top_k=3))
    assert results[0]["type"] == "infrastructure"

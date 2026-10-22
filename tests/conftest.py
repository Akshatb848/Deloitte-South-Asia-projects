"""Shared test setup.

By default the tests replace the sentence-transformers model with a small,
deterministic bag-of-words embedder so they run offline and fast. Set
RUN_MODEL_TESTS=1 to also run tests that download and use the real
`all-MiniLM-L6-v2` model (CI does this).
"""
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

# Point the LLM at a closed local port so tests never depend on Ollama.
os.environ.setdefault("OLLAMA_HOST", "http://127.0.0.1:9")
os.environ["VECTOR_DB_PATH"] = tempfile.mkdtemp(prefix="vector_db_test_")


class HashingEmbedder:
    """Deterministic stand-in for SentenceTransformer (keyword overlap only)."""

    dim = 384

    def __init__(self, *args, **kwargs):
        pass

    def encode(self, texts, **kwargs):
        out = np.zeros((len(texts), self.dim), dtype="float32")
        for row, text in enumerate(texts):
            for token in re.findall(r"[a-z0-9]+", text.lower()):
                idx = int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dim
                out[row, idx] += 1.0
            norm = np.linalg.norm(out[row])
            if norm:
                out[row] /= norm
        return out


@pytest.fixture(autouse=True)
def _fake_embedder(request, monkeypatch):
    if request.node.get_closest_marker("real_model"):
        return
    import rag.rag_system as rag_module

    monkeypatch.setattr(rag_module, "SentenceTransformer", HashingEmbedder)


def pytest_configure(config):
    config.addinivalue_line("markers", "real_model: uses the real sentence-transformers model (network)")


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_MODEL_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="set RUN_MODEL_TESTS=1 to run real-model tests")
    for item in items:
        if "real_model" in item.keywords:
            item.add_marker(skip)

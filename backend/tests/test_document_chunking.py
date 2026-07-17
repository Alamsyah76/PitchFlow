import os
import sys
from pathlib import Path

os.environ.setdefault("USE_SQLITE_DEV", "1")

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.document_service import DocumentService


def test_simple_chunk_text_always_advances_with_high_overlap():
    text = "A." + ("b" * 10000)

    chunks = DocumentService._simple_chunk_text(
        text,
        chunk_size_tokens=1,
        overlap_percent=0.99,
    )

    assert chunks
    assert chunks[-1]["content"].endswith("b")
    assert len(chunks) < len(text)


def test_simple_chunk_text_uses_prd_default_size_and_overlap():
    text = "x" * 5000

    chunks = DocumentService._simple_chunk_text(text)

    assert len(chunks) > 1
    assert all(len(chunk["content"]) <= 512 * 4 for chunk in chunks)
    assert [chunk["chunk_index"] for chunk in chunks] == list(range(len(chunks)))

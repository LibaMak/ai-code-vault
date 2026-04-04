"""Core file processing utilities for AI Code Vault.

This module handles:
- extracting text from supported uploads (.py, .txt, .pdf)
- chunking text with overlap for better semantic continuity
- generating sentence-transformer embeddings
"""

from __future__ import annotations

import io
from functools import lru_cache
from typing import Iterable

import numpy as np
from PyPDF2 import PdfReader


class FileProcessingError(Exception):
    """Raised when uploaded file parsing or embedding generation fails."""


@lru_cache(maxsize=1)
def _load_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    """Load and cache the embedding model once per process."""
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as exc:  # pragma: no cover - import error depends on environment
        raise FileProcessingError(
            "sentence-transformers is not installed or failed to import."
        ) from exc

    try:
        return SentenceTransformer(model_name)
    except Exception as exc:
        raise FileProcessingError(f"Failed to load embedding model: {model_name}") from exc


def extract_text(uploaded_file) -> str:
    """Extract text from .py, .txt, and .pdf uploads.

    Args:
        uploaded_file: Streamlit UploadedFile-like object with .name and .read().

    Returns:
        Extracted UTF-8 text.

    Raises:
        FileProcessingError: If the file is unsupported, corrupted, or unreadable.
    """
    if uploaded_file is None:
        raise FileProcessingError("No file was provided for extraction.")

    file_name = getattr(uploaded_file, "name", "") or ""
    if "." not in file_name:
        raise FileProcessingError("Uploaded file must include an extension.")

    extension = file_name.rsplit(".", 1)[-1].lower()
    if extension not in {"py", "txt", "pdf"}:
        raise FileProcessingError(
            f"Unsupported file type '{extension}'. Supported: .py, .txt, .pdf"
        )

    try:
        raw_bytes = uploaded_file.read()
    except Exception as exc:
        raise FileProcessingError("Unable to read uploaded file bytes.") from exc

    if not raw_bytes:
        raise FileProcessingError("Uploaded file is empty.")

    try:
        if extension in {"py", "txt"}:
            try:
                return raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return raw_bytes.decode("latin-1")

        pdf_reader = PdfReader(io.BytesIO(raw_bytes))
        pages = [page.extract_text() or "" for page in pdf_reader.pages]
        joined = "\n".join(pages).strip()

        if not joined:
            raise FileProcessingError(
                "PDF text extraction returned empty content. The PDF may be scanned or corrupted."
            )
        return joined

    except FileProcessingError:
        raise
    except Exception as exc:
        raise FileProcessingError("Failed to parse file content.") from exc


def chunk_data(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    """Split text into overlapping character chunks.

    Default behavior uses 700-char chunks with 100-char overlap.
    """
    if text is None:
        return []

    text = text.strip()
    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        chunk = text[start : start + chunk_size]
        if chunk:
            chunks.append(chunk)

    return chunks


def get_embeddings(text_chunks: Iterable[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
    """Convert text chunks into vector embeddings.

    Returns:
        2D numpy array with shape [num_chunks, embedding_dim].

    Raises:
        FileProcessingError: If model inference fails.
    """
    chunks = [chunk for chunk in text_chunks if chunk and chunk.strip()]
    if not chunks:
        return np.empty((0, 0), dtype=np.float32)

    model = _load_embedding_model(model_name)

    try:
        vectors = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
        return vectors.astype(np.float32)
    except Exception as exc:
        raise FileProcessingError("Failed to generate embeddings for provided chunks.") from exc

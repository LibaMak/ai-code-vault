"""Agentic AI logic for routing, retrieval, and Groq inference.

This module keeps all functions import-friendly for Streamlit integration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import numpy as np
from groq import Groq

from processor import FileProcessingError, get_embeddings


DEFAULT_ROUTER_MODEL = "llama-3.1-8b-instant"
DEFAULT_ANSWER_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODELS = ("llama-3.1-8b-instant",)
GENERAL_CHAT_ROUTE = "General Chat"
DEPRECATED_MODEL_MAP = {
    "llama3-70b-8192": DEFAULT_ANSWER_MODEL,
    "llama-3-70b-8192": DEFAULT_ANSWER_MODEL,
}


class AIServiceError(Exception):
    """Raised when AI provider config or inference fails."""


@dataclass
class RetrievedChunk:
    source: str
    text: str
    similarity: float


def _cosine_similarity(query_vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Compute cosine similarity for a single query vector against an embedding matrix."""
    if matrix.size == 0:
        return np.array([], dtype=np.float32)

    query_norm = np.linalg.norm(query_vector)
    matrix_norms = np.linalg.norm(matrix, axis=1)
    safe_denominator = np.clip(query_norm * matrix_norms, 1e-12, None)
    return (matrix @ query_vector) / safe_denominator


def _similarity_to_confidence(similarity: float) -> float:
    """Map cosine similarity in [-1, 1] into confidence percentage [0, 100]."""
    scaled = (similarity + 1.0) / 2.0
    return round(float(np.clip(scaled, 0.0, 1.0) * 100.0), 2)


def _get_groq_client(api_key: str | None = None) -> Groq:
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise AIServiceError("Missing GROQ_API_KEY. Add it to your environment or .env file.")
    return Groq(api_key=key)


def _resolve_model_name(model_name: str | None, default_model: str) -> str:
    """Resolve model name and transparently replace known deprecated IDs."""
    candidate = (model_name or "").strip()
    if not candidate:
        return default_model

    normalized = candidate.lower()
    return DEPRECATED_MODEL_MAP.get(normalized, candidate)


def _is_general_chat_query(query: str) -> bool:
    """Detect greetings and lightweight conversational prompts."""
    lowered = (query or "").strip().lower()
    if not lowered:
        return True

    direct_matches = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "how are you",
        "thanks",
        "thank you",
        "bye",
        "who are you",
        "what can you do",
    }
    if lowered in direct_matches:
        return True

    if len(lowered.split()) <= 6 and any(token in lowered for token in direct_matches):
        return True

    return False


def _invoke_with_model_fallback(
    client: Groq,
    messages: list[dict[str, str]],
    primary_model: str,
    *,
    temperature: float,
    max_tokens: int,
):
    """Call Groq chat completion and retry if a model is decommissioned."""
    models_to_try: list[str] = [_resolve_model_name(primary_model, DEFAULT_ANSWER_MODEL)]
    for fallback_model in FALLBACK_MODELS:
        resolved_fallback = _resolve_model_name(fallback_model, DEFAULT_ANSWER_MODEL)
        if resolved_fallback not in models_to_try:
            models_to_try.append(resolved_fallback)

    last_error: Exception | None = None

    for model_name in models_to_try:
        try:
            return client.chat.completions.create(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=messages,
            )
        except Exception as exc:  # pragma: no cover - API behavior varies by runtime
            last_error = exc
            error_text = str(exc).lower()
            if "decommission" in error_text or "model_decommissioned" in error_text:
                continue
            raise

    raise AIServiceError(
        f"No available Groq model could be used. Last error: {last_error}"
    )


def route_query(query: str, api_key: str | None = None) -> str:
    """Route query into one of: Search the Vault, Summarize a File, Explain Code."""
    cleaned = (query or "").strip()
    if not cleaned:
        return GENERAL_CHAT_ROUTE

    if _is_general_chat_query(cleaned):
        return GENERAL_CHAT_ROUTE

    lower = cleaned.lower()

    summarize_terms = {"summarize", "summary", "overview", "tldr", "abstract"}
    explain_code_terms = {
        "explain code",
        "what does",
        "function",
        "bug",
        "error",
        "traceback",
        "refactor",
        "optimize",
        "class",
        "method",
        "python",
        "script",
    }

    if any(term in lower for term in summarize_terms):
        return "Summarize a File"

    if any(term in lower for term in explain_code_terms):
        return "Explain Code"

    # LLM fallback for ambiguous prompts.
    try:
        client = _get_groq_client(api_key)
        router_model = _resolve_model_name(
            os.getenv("GROQ_ROUTER_MODEL", DEFAULT_ROUTER_MODEL),
            DEFAULT_ROUTER_MODEL,
        )
        response = _invoke_with_model_fallback(
            client=client,
            primary_model=router_model,
            temperature=0,
            max_tokens=12,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify user intent into exactly one label: "
                        "Search the Vault | Summarize a File | Explain Code | General Chat. "
                        "Return only the label text."
                    ),
                },
                {"role": "user", "content": cleaned},
            ],
        )
        label = (response.choices[0].message.content or "").strip()
        if label in {"Search the Vault", "Summarize a File", "Explain Code", GENERAL_CHAT_ROUTE}:
            return label
    except Exception:
        # If API is unavailable, preserve UX with deterministic fallback.
        pass

    return "Search the Vault"


def build_context_index(context_items: list[dict[str, str]]) -> dict[str, Any]:
    """Create an embedding-ready index from context rows.

    Expected input item format:
    {"source": "auth.py", "text": "...chunk content..."}
    """
    clean_items = []
    for item in context_items:
        source = (item.get("source") or "Unknown Source").strip()
        text = (item.get("text") or "").strip()
        if text:
            clean_items.append({"source": source, "text": text})

    if not clean_items:
        return {"items": [], "embeddings": np.empty((0, 0), dtype=np.float32)}

    embeddings = get_embeddings([item["text"] for item in clean_items])
    return {"items": clean_items, "embeddings": embeddings}


def retrieve_relevant_context(
    query: str,
    context_index: dict[str, Any],
    top_k: int = 3,
) -> list[RetrievedChunk]:
    """Retrieve top-k relevant chunks and attach similarity metadata."""
    items = context_index.get("items", [])
    matrix = context_index.get("embeddings", np.empty((0, 0), dtype=np.float32))

    if not items or matrix.size == 0:
        return []

    query_embedding = get_embeddings([query])
    query_vector = query_embedding[0]

    similarities = _cosine_similarity(query_vector, matrix)
    ranked_indices = np.argsort(similarities)[::-1][: max(1, top_k)]

    results: list[RetrievedChunk] = []
    for idx in ranked_indices:
        row = items[int(idx)]
        results.append(
            RetrievedChunk(
                source=row["source"],
                text=row["text"],
                similarity=float(similarities[int(idx)]),
            )
        )

    return results


def answer_with_context(
    query: str,
    context_index: dict[str, Any],
    api_key: str | None = None,
    model: str = DEFAULT_ANSWER_MODEL,
    top_k: int = 3,
) -> dict[str, Any]:
    """Run retrieval + grounded answer generation through Groq.

    Returns a structured payload suitable for Streamlit rendering.
    """
    try:
        route = route_query(query, api_key=api_key)

        if route == GENERAL_CHAT_ROUTE:
            client = _get_groq_client(api_key)
            answer_model = _resolve_model_name(model, DEFAULT_ANSWER_MODEL)
            completion = _invoke_with_model_fallback(
                client=client,
                primary_model=answer_model,
                temperature=0.3,
                max_tokens=180,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the AI Code Vault assistant. "
                            "For greetings or simple chat, reply naturally and briefly. "
                            "If asked for vault-specific answers, ask the user to upload/index files."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
            )

            answer = (completion.choices[0].message.content or "").strip()
            return {
                "ok": True,
                "route": GENERAL_CHAT_ROUTE,
                "answer": answer,
                "source": "Source: N/A (General Assistant)",
                "confidence": 100.0,
                "retrieved": [],
                "error": None,
            }

        retrieved = retrieve_relevant_context(query, context_index, top_k=top_k)

        if not retrieved:
            return {
                "ok": False,
                "route": route,
                "answer": "No relevant context found in the vault to answer this query.",
                "source": "Source: N/A",
                "confidence": 0.0,
                "error": "Context index is empty or no similar chunks were found.",
            }

        best = retrieved[0]
        confidence = _similarity_to_confidence(best.similarity)

        assembled_context = "\n\n".join(
            [f"[{item.source}]\n{item.text}" for item in retrieved]
        )

        system_prompt = (
            "You are an AI assistant for AI Code Vault. "
            "Answer strictly using only the provided context. "
            "If context is insufficient, explicitly say so. "
            "Always include a final line in this exact format: Source: <filename>."
        )

        user_prompt = (
            f"Route: {route}\n"
            f"User Query: {query}\n\n"
            f"Context:\n{assembled_context}\n\n"
            "Provide a concise, accurate answer grounded in context only."
        )

        client = _get_groq_client(api_key)
        answer_model = _resolve_model_name(model, DEFAULT_ANSWER_MODEL)
        completion = _invoke_with_model_fallback(
            client=client,
            primary_model=answer_model,
            temperature=0.2,
            max_tokens=420,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        answer = (completion.choices[0].message.content or "").strip()

        # Enforce source citation even if model omits it.
        if "source:" not in answer.lower():
            answer = f"{answer}\n\nSource: {best.source}"

        return {
            "ok": True,
            "route": route,
            "answer": answer,
            "source": f"Source: {best.source}",
            "confidence": confidence,
            "retrieved": [
                {
                    "source": item.source,
                    "similarity": round(item.similarity, 4),
                    "preview": item.text[:180],
                }
                for item in retrieved
            ],
            "error": None,
        }

    except (AIServiceError, FileProcessingError) as exc:
        return {
            "ok": False,
            "route": "Search the Vault",
            "answer": "The AI service is currently unavailable.",
            "source": "Source: N/A",
            "confidence": 0.0,
            "error": str(exc),
        }
    except Exception as exc:  # pragma: no cover - external service/runtime variability
        message = str(exc)
        if "decommission" in message.lower() or "model_decommissioned" in message.lower():
            message = (
                "Configured Groq model is deprecated. "
                "Use GROQ_MODEL=llama-3.3-70b-versatile or leave it unset."
            )
        return {
            "ok": False,
            "route": "Search the Vault",
            "answer": "An unexpected error occurred while generating the response.",
            "source": "Source: N/A",
            "confidence": 0.0,
            "error": f"Unexpected AI error: {message}",
        }

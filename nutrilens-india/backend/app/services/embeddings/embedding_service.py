"""
Gemini text-embedding-004 service.
768-dimensional embeddings for semantic food search.
"""
import asyncio
import time
from typing import List
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.gemini_api_key)

EMBEDDING_MODEL = "models/text-embedding-004"
EMBEDDING_DIM = 768
_RATE_LIMIT_DELAY = 0.1   # 100 ms between calls to avoid 429s


def embed_text_sync(text: str, task_type: str = "retrieval_document") -> List[float]:
    """Synchronous embedding — used by the import script."""
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type=task_type,
    )
    return result["embedding"]


async def embed_text(text: str, task_type: str = "retrieval_document") -> List[float]:
    """Async wrapper — used by API routes at inference time."""
    loop = asyncio.get_event_loop()
    vec = await loop.run_in_executor(None, lambda: embed_text_sync(text, task_type))
    return vec


async def embed_query(text: str) -> List[float]:
    """Embed a user query (uses retrieval_query task type for better ANN accuracy)."""
    return await embed_text(text, task_type="retrieval_query")


def batch_embed_sync(texts: List[str], task_type: str = "retrieval_document",
                     delay: float = _RATE_LIMIT_DELAY) -> List[List[float]]:
    """
    Batch synchronous embedding with rate-limit backoff.
    Used exclusively by the import script.
    """
    vectors = []
    for i, text in enumerate(texts):
        try:
            vec = embed_text_sync(text, task_type)
            vectors.append(vec)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = min(60, delay * (2 ** (i % 5)))
                print(f"  Rate limit hit, waiting {wait:.1f}s…")
                time.sleep(wait)
                vec = embed_text_sync(text, task_type)
                vectors.append(vec)
            else:
                print(f"  Embed failed for text '{text[:40]}': {e}")
                vectors.append([0.0] * EMBEDDING_DIM)
        time.sleep(delay)
    return vectors

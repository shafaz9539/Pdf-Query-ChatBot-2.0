import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai
from src.configs.settings import GENAI_API_KEY

client = genai.Client(api_key=GENAI_API_KEY)  # GENAI_API_KEY must be set


# --- Approximate tokens BEFORE calling Gemini ---
def approx_token_count(text: str) -> int:
    return len(text) // 4   # Gemini ≈ 4 chars per token


# --- Exact count ONLY when necessary ---
def exact_token_count(text: str, model: str) -> int:
    return client.models.count_tokens(
        model=model,
        contents=text
    ).total_tokens


def resplit_until_safe(text: str, model: str, max_tokens: int):
    """
    Recursively split until chunk <= max_tokens.
    Uses approx -> exact hybrid token logic for optimization.
    """
    safe_chunks = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        length_function=len
    )

    parts = splitter.split_text(text)

    for chunk in parts:
        # 1️⃣ FAST check (no API call)
        approx = approx_token_count(chunk)

        if approx > max_tokens:
            # Might be too big → split recursively
            safe_chunks.extend(resplit_until_safe(chunk, model, max_tokens))
            continue

        # 2️⃣ SAFE: exact check ONLY if approx is near the limit
        if approx > (max_tokens * 0.7):
            exact = exact_token_count(chunk, model)

            if exact > max_tokens:
                safe_chunks.extend(resplit_until_safe(chunk, model, max_tokens))
                continue

            token_count = exact
        else:
            token_count = approx   # approx safe since much smaller

        safe_chunks.append({
            "chunk_id": str(uuid.uuid4()),
            "text": chunk,
            "token_count": token_count
        })

    return safe_chunks



def chunk_with_token_safety(
    cleaned_pages: list,
    model: str = "gemini-2.0-flash",
    max_tokens: int = 800,
    chunk_size: int = 1200,
    chunk_overlap: int = 200
):
    """
    Hybrid token-based safe chunking:
      - LangChain splits first
      - Approx token count first (FAST)
      - Exact Gemini check only if needed (OPTIMIZED)
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    final_chunks = []

    for page in cleaned_pages:
        page_num = page["page_number"]
        text = page["text"]

        raw_chunks = splitter.split_text(text)

        for chunk_text in raw_chunks:

            # 1️⃣ Approx count (instant, no API call)
            approx = approx_token_count(chunk_text)

            if approx > max_tokens:
                # too big → re-split
                safe_parts = resplit_until_safe(chunk_text, model, max_tokens)
                for sp in safe_parts:
                    final_chunks.append({
                        "chunk_id": sp["chunk_id"],
                        "page_number": page_num,
                        "text": sp["text"],
                        "token_count": sp["token_count"]
                    })
                continue

            # 2️⃣ When approx is near limit → exact check
            if approx > (max_tokens * 0.7):
                exact = exact_token_count(chunk_text, model)
                token_count = exact
                if exact > max_tokens:
                    safe_parts = resplit_until_safe(chunk_text, model, max_tokens)
                    for sp in safe_parts:
                        final_chunks.append({
                            "chunk_id": sp["chunk_id"],
                            "page_number": page_num,
                            "text": sp["text"],
                            "token_count": sp["token_count"]
                        })
                    continue
            else:
                # small enough → approx is fine
                token_count = approx

            final_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "page_number": page_num,
                "text": chunk_text,
                "token_count": token_count
            })

    print(f"✅ Created {len(final_chunks)} final chunks.")
    return final_chunks

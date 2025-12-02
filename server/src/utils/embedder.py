from google import genai
from google.genai import types
import time
from ..core.config import settings
from ..utils.normalize_vector import normalize

client = genai.Client(api_key=settings.GENAI_API_KEY)

MODEL_NAME = "gemini-embedding-001"
BATCH_SIZE = 96  


def embed_chunks(chunks: list[str], batch_size: int = BATCH_SIZE):
    all_embeddings = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        content_list = [
            types.Content(parts=[types.Part(text=chunk)])
            for chunk in batch
        ]

        for attempt in range(3):
            try:
                response = client.models.embed_content(
                    model=MODEL_NAME,
                    contents=content_list,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=1536)

                )   

                normalized_vectors = [normalize(emb.values) for emb in response.embeddings]

                all_embeddings.extend(normalized_vectors)

                break

            except Exception as e:
                print(f"⚠ Gemini embed failed (attempt {attempt+1}/3): {e}")
                time.sleep(1 + attempt * 1)

        else:
            raise RuntimeError("Gemini embedding failed after 3 retries.")

    print(f"✅ Embedded {len(chunks)} chunks into {len(all_embeddings)} embeddings.")
    return all_embeddings



def embed_query(text: str):
    """Embed a single query text for RAG."""
    text = text.strip()

    content = types.Content(parts=[types.Part(text=text)])

    response = client.models.embed_content(
        model=MODEL_NAME,   
        contents=[content],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", output_dimensionality=1536)
    )


    if not response.embeddings:
        raise RuntimeError("No embedding returned from Gemini.")

    return normalize(response.embeddings[0].values)

from google import genai
from ..core.config import settings

client = genai.Client(api_key=settings.GENAI_API_KEY)


def generate_answer(question: str, context: str):
    prompt = f"""
You are a factual RAG question-answering assistant.

You MUST answer strictly and only from the provided context.

If the answer is not present in the context,
respond exactly with: "I cannot find the answer in the document."

---

CONTEXT:
{context}

---

QUESTION:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    )

    return response.text

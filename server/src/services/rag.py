from google import genai
from src.configs.settings import GENAI_API_KEY

client = genai.Client(api_key=GENAI_API_KEY)


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
        model="gemini-2.5-pro",
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

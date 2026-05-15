import json
import re 
from typing import Iterable
import ollama
from src.config import settings

def embed_text(text: str) -> list[float]:

    response = ollama.embed(
        model=settings.EMBED_MODEL,
        input=text
    )
    return response["embeddings"][0]

def embed_texts(texts: Iterable[str]) -> list[list[float]]:
    embeddings: list[list[float]] = []

    for index, text in enumerate(texts, start=1):
        print(f"Creating embeddings {index}...")
        embeddings.append(embed_text(text))

    return embeddings

def chat(prompt: str, temperature: float = 0.0) -> str:
    response = ollama.chat(model=settings.LLM_MODEL,
                            messages=[{
                                "role": "user",
                                "content": prompt,
                            }],
                            options={
                                "temperature": temperature
                            })
    
    return response["message"]["content"]

def extract_json_object(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
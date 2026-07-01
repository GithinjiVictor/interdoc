import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq 
# from openai import OpenAI 

# import functions from the python-dotenv library. This function reads a file called .env
load_dotenv(dotenv_path=Path(__file__).parent / ".env")
client = Groq(api_key=os.getenv("GROQ_API_KEY")) #  Looks up the environment variables named GROQ_API_KEY

def build_prompt(question: str, chunks: list[str], metadatas: list[dict]):
    blocks = [] # to hold each chunk, 
    # (zip(chunks, metadatas) - pairs eachchunk with its metadata dict 
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas), start=1):
        blocks.append(f"[Source {i}: {meta['source']}, chunk {meta['chunk_index']}]\n{chunk}")
    context = "\n\n".join(blocks)
    # this builds and return the complete prompt. 
    return (
        "Answer the question using ONLY the context below."
        "Cite sources using [Source N]. if the answer is not in the"
        "context, say you don't have enough information - do not guess.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    )

def generate_answer(question: str, search_results: dict):

    # unpack the chromaDB result dictionary.
    chunks = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]
    # safety guard if no file uploaded 
    if not chunks:
        return {"answer": "No documents have been uploaded yet", "sources": []}
    prompt = build_prompt(question, chunks, metadatas)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    answer_text = response.choices[0].message.content 
    sources = [{"sources": m["source"], "chunk_index": m["chunk_index"]} for m in metadatas]
    # answer - The LLM'S generated response text 
    # sources - the list of source reference used to generate that answer
    return {"answer": answer_text, "sources": sources}
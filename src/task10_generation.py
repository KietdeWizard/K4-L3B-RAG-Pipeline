"""Task 10 - Generation with citation."""

import os
import re

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Answer only from the provided context.
Every factual claim must be grounded in the retrieved sources. If evidence is
missing, refuse to verify the answer."""

SAFE_REFUSAL = "I cannot verify this from the available sources."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Place strong chunks at the beginning and end without mutating input."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks with labels that can be cited by the answer."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        parts.append(
            f"[Document {index} | Title: {metadata['title']} | "
            f"Source: {metadata['source']} | Method: {chunk['retrieval_method']} | "
            f"Score: {chunk['score']:.4f}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def _local_grounded_answer(user_message: str) -> str:
    """Small offline answerer used when no external LLM key is configured."""
    context_match = re.search(r"Context:\n(.+?)\n\nQuestion:", user_message, flags=re.S)
    context = context_match.group(1).strip() if context_match else user_message
    question_match = re.search(r"\n\nQuestion:\s*(.+)\s*$", user_message, flags=re.S)
    question = question_match.group(1).strip() if question_match else ""
    query_terms = {
        token
        for token in re.findall(r"[A-Za-z][A-Za-z-]{2,}", question.lower())
        if token not in {"what", "which", "where", "when", "about", "from", "the", "and", "can"}
    }
    snippets = []
    for block in context.split("\n\n---\n\n"):
        header, _, body = block.partition("\n")
        source_match = re.search(r"Source:\s*([^|]+)", header)
        title_match = re.search(r"Title:\s*([^|]+)", header)
        source = source_match.group(1).strip() if source_match else "retrieved source"
        title = title_match.group(1).strip() if title_match else source
        body = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", body)
        body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
        lines = [
            re.sub(r"\s+", " ", line).strip(" -*")
            for line in body.splitlines()
        ]
        clean_lines = [
            line
            for line in lines
            if len(line) >= 45
            and "javascript:void" not in line.lower()
            and "vietnam tourism" not in line.lower()
            and not line.lower().startswith(("home", "places to go", "things to do"))
        ]
        clean_body = " ".join(clean_lines)
        sentences = re.split(r"(?<=[.!?])\s+", clean_body)
        scored = []
        for sentence in sentences:
            sentence_terms = set(re.findall(r"[A-Za-z][A-Za-z-]{2,}", sentence.lower()))
            overlap = len(query_terms & sentence_terms)
            if len(sentence) >= 45:
                scored.append((overlap, sentence))
        scored.sort(key=lambda pair: (pair[0], len(pair[1])), reverse=True)
        if scored:
            chosen = scored[0][1][:320]
            snippets.append(f"{title}: {chosen} [{source}]")
        if len(snippets) == 2:
            break
    if not snippets:
        return SAFE_REFUSAL
    return "Based on the retrieved corpus, the strongest evidence is: " + " ".join(snippets)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Call the configured LLM provider, falling back to a local grounded answer."""
    if LLM_PROVIDER == "openai" and os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=LLM_MODEL or "gpt-4o-mini",
            temperature=TEMPERATURE,
            top_p=TOP_P,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or SAFE_REFUSAL

    if LLM_PROVIDER == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        from anthropic import Anthropic

        client = Anthropic()
        response = client.messages.create(
            model=LLM_MODEL or "claude-3-5-haiku-latest",
            temperature=TEMPERATURE,
            top_p=TOP_P,
            max_tokens=600,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return "".join(block.text for block in response.content if getattr(block, "type", "") == "text") or SAFE_REFUSAL

    if LLM_PROVIDER == "gemini" and os.getenv("GEMINI_API_KEY"):
        from google import genai

        client = genai.Client()
        response = client.models.generate_content(
            model=LLM_MODEL or "gemini-2.5-flash",
            contents=f"{system_prompt}\n\n{user_message}",
        )
        return response.text or SAFE_REFUSAL

    return _local_grounded_answer(user_message)


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Return a GenerationResult with answer, sources and retrieval_source."""
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": SAFE_REFUSAL,
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception:
        answer = SAFE_REFUSAL

    retrieval_method = chunks[0]["retrieval_method"]
    retrieval_source = "pageindex" if retrieval_method == "pageindex" else "hybrid"
    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    print(generate_with_citation("What can visitors do in Hoi An?"))

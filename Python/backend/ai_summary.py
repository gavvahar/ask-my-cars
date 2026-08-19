import os, anthropic, httpx

from .analytics import kpis


def _build_prompt(filtered_df):
    stats = kpis.compute_kpis(filtered_df)
    dominant_make = filtered_df["make"].mode()[0]
    return (
        f"Dataset: {stats['count']} vehicles, average highway MPG {stats['avg_mpg']}, "
        f"average horsepower {stats['avg_hp']}, most common make {dominant_make}, "
        f"model years {filtered_df['year'].min()}-{filtered_df['year'].max()}. "
        "Write one friendly, conversational paragraph summarizing this filtered "
        "car dataset for someone browsing a dashboard, e.g. \"You're looking at "
        '42 SUVs from 2005-2012 averaging 22 MPG..."'
    )


def _call_anthropic(prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        thinking={"type": "disabled"},
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": prompt}],
    )
    return next((b.text for b in response.content if b.type == "text"), "")


def _call_ollama(prompt):
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL")
    if not model:
        raise RuntimeError("OLLAMA_MODEL is not set")

    try:
        response = httpx.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"num_predict": 300},
            },
            timeout=90,
        )
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise ConnectionError(f"Ollama request failed: {e}") from e

    return response.json()["message"]["content"]


def generate_summary(filtered_df):
    prompt = _build_prompt(filtered_df)
    provider = os.environ.get("AI_SUMMARY_PROVIDER", "anthropic")

    if provider == "ollama":
        return _call_ollama(prompt)
    return _call_anthropic(prompt)

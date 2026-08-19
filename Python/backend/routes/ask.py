from fastapi import APIRouter, HTTPException

from ..rag.citations import CITATION_PATTERN
from ..rag.graph import build_graph

router = APIRouter()

_graph = build_graph()


@router.post("/api/ask")
def ask(body: dict):
    question = body.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="A question is required.")

    try:
        result = _graph.invoke({"question": question})
    except Exception as err:
        raise HTTPException(status_code=502, detail="The AI service is unavailable right now.") from err

    answer = result.get("answer", "")
    documents = result.get("documents", [])
    cited_ids = [int(match) for match in CITATION_PATTERN.findall(answer)]

    return {
        "answer": answer,
        "route": result.get("route"),
        "cited_car_ids": cited_ids,
        "retrieved_cars": [document.metadata for document in documents],
    }

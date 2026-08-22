import os, psycopg
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError

from ..rag.citations import extract_citation_ids
from ..rag.graph import build_graph

router = APIRouter()

_graph = build_graph()
_executor = ThreadPoolExecutor(max_workers=4)

REQUEST_TIMEOUT_SECONDS = int(os.environ.get("ASK_TIMEOUT_SECONDS", "120"))


@router.post("/api/ask")
def ask(body: dict):
    question = body.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="A question is required.")

    future = _executor.submit(_graph.invoke, {"question": question})
    try:
        result = future.result(timeout=REQUEST_TIMEOUT_SECONDS)
    except FutureTimeoutError as err:
        raise HTTPException(
            status_code=504,
            detail="This is taking longer than expected on our self-hosted setup. Please try again.",
        ) from err
    except (psycopg.OperationalError, SQLAlchemyOperationalError) as err:
        raise HTTPException(
            status_code=503,
            detail="Our database is temporarily unavailable. Please try again shortly.",
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=502,
            detail="The AI service is unavailable right now. Please try again in a moment.",
        ) from err

    answer = result.get("answer", "")
    documents = result.get("documents", [])
    cited_ids = [int(match) for match in extract_citation_ids(answer)]

    return {
        "answer": answer,
        "route": result.get("route"),
        "cited_car_ids": cited_ids,
        "retrieved_cars": [document.metadata for document in documents],
    }

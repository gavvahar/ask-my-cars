import re

CITATION_PATTERN = re.compile(r"\[Car ID:\s*([^\]]+)\]")


def _split_ids(raw):
    return [part.strip() for part in raw.split(",") if part.strip()]


def extract_citation_ids(answer):
    ids = []
    for raw in CITATION_PATTERN.findall(answer):
        ids.extend(_split_ids(raw))
    return ids


def validate_citations(answer, documents):
    valid_ids = {str(document.metadata["id"]) for document in documents}
    hallucinated_ids = []

    def _replace(match):
        cited_ids = _split_ids(match.group(1))
        kept_ids = [cited_id for cited_id in cited_ids if cited_id in valid_ids]
        hallucinated_ids.extend(cited_id for cited_id in cited_ids if cited_id not in valid_ids)
        if not kept_ids:
            return "[citation removed]"
        return f"[Car ID: {', '.join(kept_ids)}]"

    cleaned_answer = CITATION_PATTERN.sub(_replace, answer)
    return {"answer": cleaned_answer, "hallucinated_ids": hallucinated_ids}


if __name__ == "__main__":
    from langchain_core.documents import Document

    documents = [
        Document(page_content="A real car.", metadata={"id": 1}),
        Document(page_content="Another real car.", metadata={"id": 2}),
    ]

    fake_answer = "The 2016 Toyota Prius [Car ID: 1] is a great choice. You might also like this car [Car ID: 999], which doesn't actually exist in our results."

    result = validate_citations(fake_answer, documents)
    print("Cleaned answer:", result["answer"])
    print("Hallucinated ids caught:", result["hallucinated_ids"])
    assert result["hallucinated_ids"] == ["999"], "Expected to catch the fake citation"
    assert "[Car ID: 1]" in result["answer"], "Expected the real citation to survive"
    print("OK - hallucinated citation caught and stripped, real citation preserved.")

    bundled_answer = "Check out [Car ID: 1, 2] and also [Car ID: 2, 999]."
    bundled_result = validate_citations(bundled_answer, documents)
    print("Bundled cleaned answer:", bundled_result["answer"])
    print("Bundled hallucinated ids caught:", bundled_result["hallucinated_ids"])
    assert bundled_result["hallucinated_ids"] == ["999"], "Expected only the fake id in a bundle to be caught"
    assert "[Car ID: 1, 2]" in bundled_result["answer"], "Expected the fully-valid bundle to survive untouched"
    assert "[Car ID: 2]" in bundled_result["answer"], "Expected the partially-valid bundle to keep only the real id"
    print("OK - bundled citations are split and validated individually.")

    invented_answer = "The 2014-2016 Bentley Flying Spur [Car ID: 2014-2016 Bentley Flying Spur] is lovely."
    invented_result = validate_citations(invented_answer, documents)
    print("Invented-id cleaned answer:", invented_result["answer"])
    print("Invented-id hallucinated ids caught:", invented_result["hallucinated_ids"])
    assert invented_result["hallucinated_ids"] == ["2014-2016 Bentley Flying Spur"], "Expected the invented non-numeric id to be caught"
    assert "[citation removed]" in invented_result["answer"], "Expected the invented citation to be stripped"
    print("OK - invented non-numeric citations are caught and stripped too.")

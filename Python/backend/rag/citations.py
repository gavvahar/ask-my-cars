import re

CITATION_PATTERN = re.compile(r"\[Car ID:\s*(\d+)\]")


def validate_citations(answer, documents):
    valid_ids = {str(document.metadata["id"]) for document in documents}
    hallucinated_ids = []

    def _replace(match):
        cited_id = match.group(1)
        if cited_id in valid_ids:
            return match.group(0)
        hallucinated_ids.append(cited_id)
        return "[citation removed]"

    cleaned_answer = CITATION_PATTERN.sub(_replace, answer)
    return {"answer": cleaned_answer, "hallucinated_ids": hallucinated_ids}


if __name__ == "__main__":
    from langchain_core.documents import Document

    documents = [
        Document(page_content="A real car.", metadata={"id": 1}),
        Document(page_content="Another real car.", metadata={"id": 2}),
    ]

    fake_answer = (
        "The 2016 Toyota Prius [Car ID: 1] is a great choice. "
        "You might also like this car [Car ID: 999], which doesn't actually exist in our results."
    )

    result = validate_citations(fake_answer, documents)
    print("Cleaned answer:", result["answer"])
    print("Hallucinated ids caught:", result["hallucinated_ids"])
    assert result["hallucinated_ids"] == ["999"], "Expected to catch the fake citation"
    assert "[Car ID: 1]" in result["answer"], "Expected the real citation to survive"
    print("OK - hallucinated citation caught and stripped, real citation preserved.")

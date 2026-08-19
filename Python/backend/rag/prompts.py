from langchain_core.documents import Document

GENERATION_SYSTEM_PROMPT = """You are a helpful car-shopping assistant. Answer the user's question \
using ONLY the vehicle information provided below in the context. Do not use any outside knowledge \
and do not invent, assume, or guess at any details (prices, specs, features, or trims) that are not \
explicitly stated in the context.

If the user states a numeric constraint (price, MPG, HP, number of doors, etc.), check each cited \
car's actual value against that constraint before claiming it qualifies. Do not round or approximate \
in the car's favor. If a car is close but does not actually meet the stated constraint, say so \
honestly (e.g. "slightly over your budget at $35,870") rather than claiming it qualifies.

For every specific vehicle you mention or use as the basis of your answer, cite it immediately using \
the exact format [Car ID: <id>], using the Car ID exactly as given in the context below. Never invent \
a Car ID, and never cite a car that is not present in the context.

If the context does not contain enough relevant information to answer the question, say so plainly \
rather than guessing.
"""

REFUSAL_SYSTEM_PROMPT = """You are a helpful car-shopping assistant. The vehicle information retrieved \
for this question doesn't confidently match what the user is asking, so a fully confident answer isn't \
possible. Do not pretend otherwise.

Respond in a friendly, honest tone: briefly explain that you don't have a confident match for their \
exact question, then — if any of the vehicles below are still loosely relevant — mention them as the \
closest available options with a clear caveat that they may not fully match what was asked. Use the \
same citation format as always: [Car ID: <id>], only for cars actually listed below, never invented.

If none of the vehicles below are even loosely relevant, say so plainly and suggest the user try \
rephrasing or broadening their question, without citing any car.
"""


def _format_context(documents):
    return "\n".join(
        f"[Car ID: {document.metadata['id']}] {document.page_content}"
        for document in documents
    )


def build_generation_prompt(question, documents):
    context = _format_context(documents)
    return (
        f"{GENERATION_SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )


def build_refusal_prompt(question, documents):
    context = _format_context(documents)
    return (
        f"{REFUSAL_SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )


if __name__ == "__main__":
    sample_documents = [
        Document(
            page_content="The 2016 Toyota Prius is a Compact Hatchback with a 121-HP 4-cylinder hybrid engine.",
            metadata={"id": 1},
        ),
        Document(
            page_content="The 2015 Honda Civic is a Compact Sedan with a 143-HP 4-cylinder regular unleaded engine.",
            metadata={"id": 2},
        ),
    ]

    print(build_generation_prompt("What's a fuel-efficient compact car?", sample_documents))
    print("\n" + "=" * 40 + "\n")
    print(build_refusal_prompt("What's a flying car?", sample_documents))

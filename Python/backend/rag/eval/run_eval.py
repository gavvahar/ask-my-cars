from ..citations import extract_citation_ids
from ..graph import build_graph

QUESTIONS = [
    ("factual", "What are the specs of the 2011 BMW 1 Series M?"),
    ("factual", "Tell me about the Toyota Corolla."),
    ("factual", "What is the horsepower of the Porsche Carrera GT?"),
    ("semantic", "I need a reliable family SUV that won't break the bank."),
    ("semantic", "What's a good car for a long highway commute?"),
    ("semantic", "Show me something sporty and fast."),
    ("semantic", "I want a practical car for city driving with good gas mileage."),
    ("semantic", "What luxury sedans do you have?"),
    ("refusal", "Do you have any electric scooters?"),
    ("refusal", "What about flying cars or teleportation pods?"),
    ("refusal", "Can you recommend a good motorcycle?"),
    ("ambiguous", "What's the best car?"),
    ("ambiguous", "Tell me about a good one."),
    ("numeric_boundary", "I need an SUV under $36,000."),
    ("aggregate_stress", "What's the cheapest car in your database?"),
]


def run_eval():
    graph = build_graph()

    for category, question in QUESTIONS:
        result = graph.invoke({"question": question})
        answer = result.get("answer", "")
        cited_ids = extract_citation_ids(answer)

        print(f"=== [{category}] {question}")
        print(f"route: {result.get('route')}")
        print(f"hallucinated_ids: {result.get('hallucinated_ids')}")
        print(f"cited_ids: {cited_ids}")
        print(f"retrieved_count: {len(result.get('documents', []))}")
        print(f"answer: {answer}")
        print()


if __name__ == "__main__":
    run_eval()

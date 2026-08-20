# Ask My Cars

A standalone RAG app for the [car-specs-explorer](https://github.com/gavvahar/car-specs-explorer) dataset (~11,801-row Kaggle "Car Features and MSRP" data) — ask natural-language questions like "fuel-efficient family SUV under $35k" and get a grounded, cited answer referencing specific real vehicles. Extends Week 1's dataset and concept with semantic search, built with LangChain/LangGraph and a self-hosted Ollama model (`qwen2.5:7b` generation, `embeddinggemma` embeddings) — no external API dependency.

This is a fresh, standalone build, not a fork of car-specs-explorer's dashboard code — it reuses the same dataset and cleaning logic (`data_utils.py`), but the RAG search feature here is new.

## Setup

1. Clone the repo.
2. Copy `.env.example` to `.env` and fill in a `POSTGRES_PASSWORD`. The Ollama variables already default to the project's own self-hosted instance — override `OLLAMA_BASE_URL` if you're running your own.
3. Get the dataset (not committed to the repo):
   - Kaggle CLI: `kaggle datasets download -d CooperUnion/cardataset -p data/ --unzip` (may require Kaggle API credentials at `~/.kaggle/kaggle.json`)
   - Manual: download from https://www.kaggle.com/datasets/CooperUnion/cardataset
   - Either way, place/rename the resulting CSV as `data/cars.csv`.

## Running

Everything runs via Docker Compose. This is a one-time setup (seed + embed) followed by starting the app.

**1. Bring up Postgres:**

```
docker compose up postgres -d
```

**2. Seed the database** (one-time — loads and cleans the dataset, creates the `cars` table and the full-text search index, ~11,801 rows):

```
docker compose --profile seed run --rm seed
```

**3. Build embeddings** (one-time — embeds every row via the self-hosted Ollama instance and writes into pgvector. Checkpointed/resumable if interrupted. Took ~82 minutes for the full dataset in testing, CPU-only):

```
docker compose run --rm app python -m scripts.build_embeddings
```

**4. Start the app:**

```
docker compose up app -d
```

Then visit http://localhost:8001.

Steps 2 and 3 only need to run once — after that, `docker compose up app -d` (and `postgres`, if not already running) is all that's needed. Re-running the seed script is safe (idempotent, `TRUNCATE`+reload) but will require re-running the embedding build afterward, since it clears the table `build_embeddings.py` checkpoints against.

## Architecture

### Corpus & Ingestion

The corpus is the same structured car dataset used in the Week 1 dashboard (make, model, year, engine specs, drivetrain, category, size, style, MPG, popularity, MSRP — 17 columns, 11,801 rows after cleaning). Each row is converted into a natural-language document (`rag/documents.py::build_description`) rather than exposed as raw structured data, since the retrieval layer needs prose to embed and full-text search meaningfully — e.g. "2011 BMW 1 Series M, a compact coupe with a 335 HP twin-turbo inline-6..." rather than a raw column dump.

Ingestion (`scripts/build_embeddings.py`) runs in batches of 500 against a self-hosted Ollama embedding model (`embeddinggemma`), writing into `pgvector` via `langchain_postgres.PGVector`. Idempotency is handled two ways: `PGVector.add_documents(..., ids=ids)` performs an `INSERT ... ON CONFLICT (id) DO UPDATE` upsert (verified directly against the source, then empirically confirmed via a re-run producing zero duplicates), and an `embedded_at` bookkeeping column lets the build script skip already-embedded rows on resume.

### Retrieval Strategy: Hybrid Dense + Sparse

Two retrievers run in parallel and get fused via `EnsembleRetriever` (weighted 0.6 dense / 0.4 sparse):

- **Dense**: pgvector cosine similarity over the Ollama embeddings — good for semantic/fuzzy queries ("something sporty and fast") that share no vocabulary with the corpus text.
- **Sparse**: Postgres full-text search (`tsvector`/GIN index/`websearch_to_tsquery`) over the structured columns — good for exact factual lookups (make/model/year) where dense retrieval can drift toward "similar in spirit" instead of "the actual car asked about."

This is deliberately not dense-only: early testing showed sparse retrieval returning 0 results on realistic conversational queries, traced to `websearch_to_tsquery`'s implicit AND semantics — any filler word not present in the structured columns zeroed out an otherwise-good match. Fixed by OR-joining query terms before passing to `websearch_to_tsquery` (`rag/fts_search.py::_build_or_query`); re-verified end-to-end, sparse went from 0/8 to 8/8 genuine results on the original failing query.

### Confidence Routing & Refusal

`rag/graph.py` routes each question through a `retrieve → {generate | refuse} → validate` graph. Confidence is scored via `vectorstore.similarity_search_with_score()` (raw cosine distance, since `EnsembleRetriever` discards scores after rank fusion) against a calibrated threshold (0.6 — in-corpus queries scored 0.43–0.58, out-of-corpus 0.63–0.83 during calibration). Below-threshold questions route to a `refuse` node that still surfaces the nearest matches with an honest caveat, rather than a bare "I don't know."

### Citation & Faithfulness Guard

Generated answers cite cars in a `[Car ID: <id>]` format, chosen specifically for reliable regex validation over fuzzy prose matching. `rag/citations.py::validate_citations()` strips any cited ID that isn't actually in the retrieved document set, logging what it caught — this is the app's only defense against hallucinated citations, and it runs on every request via the graph's `validate` node.

A separate faithfulness class of bug — the model correctly citing a _real_ car but misstating a _fact_ about it — was caught earlier in development (a $35,870 SUV described as "under $35k") and fixed via an explicit numeric-verification instruction in the generation system prompt, not via the citation validator (which only checks that a cited ID exists, not that claims about it are accurate).

## Evaluation

**Methodology**: 15 hand-crafted questions across 5 categories (factual lookup, semantic/fuzzy, refusal-trigger, ambiguous, plus a deliberate near-boundary numeric case and an aggregate/superlative stress test), each scored manually on a 3-point scale (Poor/Adequate/Good) for retrieval quality and answer quality, and Pass/Fail for faithfulness. Faithfulness scoring is seeded by `citations.py`'s `hallucinated_ids` output (read directly off the compiled graph's state, not the HTTP API) as a free automated signal, with a manual spot-check on top since the validator only catches hallucinated _citations_, not hallucinated _claims about real citations_. The question set and runner live in `Python/backend/rag/eval/run_eval.py`.

**Results** (run against the full 11,801-row corpus, live):

| #   | Category         | Question                                  | Route    | Retrieval | Faithfulness | Answer Quality | Notes                                                                                         |
| --- | ---------------- | ----------------------------------------- | -------- | --------- | ------------ | -------------- | --------------------------------------------------------------------------------------------- |
| 1   | factual          | 2011 BMW 1 Series M specs                 | generate | Good      | Pass         | Good           | Clean, exact match                                                                            |
| 2   | factual          | Toyota Corolla                            | generate | Good      | Pass*        | Good           | *Citation extraction failed on multi-ID bracket                                               |
| 3   | factual          | Porsche Carrera GT horsepower             | generate | Good      | Pass         | Good           | Concise, correct (605 HP), well-cited                                                         |
| 4   | semantic         | reliable family SUV, won't break the bank | generate | Good      | Pass         | Good           | Mitsubishi Outlander, well-cited                                                              |
| 5   | semantic         | long highway commute                      | refuse   | Adequate  | Pass         | Adequate       | Honest mismatch admission                                                                     |
| 6   | semantic         | sporty and fast                           | refuse   | Poor      | Pass         | Adequate       | Weak match, honestly hedged                                                                   |
| 7   | semantic         | practical city car, good gas mileage      | generate | Good      | Pass         | Good           | Honda Insight hybrid                                                                          |
| 8   | semantic         | luxury sedans                             | refuse   | Good      | Pass         | Good           | 5 real matches — arguably should've generated; threshold-tuning candidate                     |
| 9   | refusal          | electric scooters                         | refuse   | N/A       | Pass         | Good           | Clean refusal                                                                                 |
| 10  | refusal          | flying cars / teleportation pods          | refuse   | N/A       | Pass*        | Adequate       | *Worst citation case — invented a non-numeric pseudo-ID                                       |
| 11  | refusal          | good motorcycle                           | refuse   | N/A       | Pass         | Good           | Cleanest refusal of the three                                                                 |
| 12  | ambiguous        | best car                                  | refuse   | Adequate  | Pass         | Good           | Genuine ambiguity, asks clarifying questions                                                  |
| 13  | ambiguous        | tell me about a good one                  | refuse   | Poor      | Pass         | Adequate       | Honest given vagueness                                                                        |
| 14  | numeric_boundary | SUV under $36,000                         | generate | Good      | Pass*        | Good           | Faithfulness fix holds under real retrieval; *citation extraction failed (no brackets at all) |
| 15  | aggregate_stress | cheapest car in database                  | refuse   | Adequate  | Pass         | Good           | Honest — can't guarantee true corpus-wide MIN via top-k retrieval                             |

**Headline results**:

- **Zero actual hallucinations across all 15 questions** — `hallucinated_ids` came back empty every time; the citation validator never had to strip anything.
- **The numeric-faithfulness fix holds under real, non-forced retrieval.** Q14 is the first test of the $35,870-Buick-Envision fix outside the original forced-reproduction retest (which had to inject the exact bug-triggering documents directly to bypass retrieval's non-determinism); it passed cleanly here under genuine live retrieval.
- **The aggregate-query stress test (Q15) worked as designed.** Top-k retrieval structurally can't answer "what's the cheapest car in the whole database" — the system surfaced that honestly instead of confidently hallucinating a wrong answer, which was the point of including it.

## Known Limitations / Future Work

**Citation extraction is unreliable (~3/15 questions), independent of citation _correctness_.** The `[Car ID: <id>]` format is not consistently followed by the generation model:

- Multiple IDs bundled into one bracket (`[Car ID: 2944, 2942, ...]`) — the extraction regex expects exactly one numeric ID per bracket, so these citations are silently dropped rather than parsed.
- Brackets omitted entirely in one response, despite the answer content being accurate.
- One case invented a non-numeric pseudo-ID (`[Car ID: 2014-2016 Bentley Flying Spur]`) — not something a regex fix alone can catch, since it's a format-adherence failure, not a parsing gap.

Practical effect: broken/missing citation badges and highlighted car cards in the frontend for these responses, even though the underlying answers were factually accurate in every case observed. This is a UI/attribution-completeness issue, not a correctness or hallucination issue.

This also exposes a blind spot in the automated faithfulness check: `hallucinated_ids` only evaluates _extracted_ IDs, so when extraction fails outright, the check trivially reports "Pass" without having verified anything. The eval methodology's manual spot-check step was designed to cover exactly this gap, and did — this is the check working as intended, not a check that failed.

Logged as a known limitation rather than fixed in this pass. If picked up later, worth trying a more lenient extraction regex (split on commas within a bracket) as a cheap partial fix for the bundled-ID case, though the invented-pseudo-ID case would still need a prompt-level fix.

**Secondary, minor**: Q8 ("luxury sedans") retrieved 5 well-matched, well-cited results but still routed to `refuse` — a threshold-tuning observation, not a bug; the 0.6 confidence cutoff may be marginally conservative for broad-category semantic queries. Not changed in this pass.

## License

MIT — see [LICENSE](LICENSE).

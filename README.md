# Car Specs & MPG Dashboard

A Streamlit dashboard for exploring car specs — horsepower, MPG, and price — built on Kaggle's "Car Features and MSRP" dataset (~11k vehicles, model years 1990-2017).

**Status: feature-complete.** Data loading/cleaning, sidebar filters (Make / Year / Fuel Type), a KPI row, four charts (Horsepower vs. Highway MPG with hover tooltips, Avg Highway MPG by Vehicle Style, Horsepower vs. MSRP, and Horsepower/MPG trends by model year), and a Top 10 efficiency leaderboard are all built, with empty-state handling throughout. The optional AI-generated natural-language summary stretch goal is also implemented, gated on an ANTHROPIC_API_KEY being present.

## Setup

1. Clone the repo.
2. Create/activate the `car` conda environment: `conda env create -f environment.yml` (or `conda activate car` if it already exists).
3. Install dependencies: `pip install -r requirements.txt`.
4. (Optional) For the AI summary feature, copy `.env.example` to `.env` and configure:
   - `ANTHROPIC_API_KEY` — required if using the default Anthropic provider.
   - `AI_SUMMARY_PROVIDER` — `anthropic` (default) or `ollama`.
   - `OLLAMA_BASE_URL` — only used when provider is `ollama`; defaults to `http://localhost:11434`.
   - `OLLAMA_MODEL` — required when provider is `ollama` (no default — must match a model already pulled on your Ollama instance).

## Dataset

The dataset isn't committed to the repo. Get it one of two ways:

- Kaggle CLI: `kaggle datasets download -d CooperUnion/cardataset -p data/ --unzip` (may require Kaggle API credentials at `~/.kaggle/kaggle.json` — generate one from your Kaggle account settings if the download prompts for auth)
- Manual: download from https://www.kaggle.com/datasets/CooperUnion/cardataset

Either way, place/rename the resulting CSV as `data/cars.csv`.

## Running

From the repo root:

```
streamlit run Python/app.py
```

## FastAPI Backend

This branch also includes a FastAPI + server-rendered frontend, replacing the Streamlit app as the primary interface.

From the repo root:

```
cd Python
uvicorn backend.main:app --reload --port 8000
```

Then visit http://localhost:8000.

## Docker / Podman

Build:

```
docker build -t car-specs-explorer .
```

Run (the dataset isn't baked into the image — mount it at runtime instead, so the build doesn't need Kaggle credentials):

```
docker run -p 8000:8000 -v $(pwd)/data:/app/data car-specs-explorer
```

Podman works as a drop-in replacement — swap `docker` for `podman` in both commands. One caveat: on SELinux-enabled systems (e.g. Fedora/RHEL), rootless Podman bind mounts sometimes need an SELinux relabel suffix to avoid permission-denied errors:

```
podman run -p 8000:8000 -v $(pwd)/data:/app/data:Z car-specs-explorer
```

Only add `:Z` if you actually hit that error — it's unnecessary on non-SELinux systems.

Or, with Docker Compose:

```
docker compose up --build
```

That's the simplest path if you don't need the manual build/run split — same port and volume mount as the commands above, driven from `compose.yaml`. Note: `compose.yaml` references a `.env` file directly, and not every Compose implementation treats that as optional — create an empty `.env` if you don't need the AI summary feature and `docker compose up` complains about a missing file.

The container serves the FastAPI backend — visit http://localhost:8000.

## License

MIT — see [LICENSE](LICENSE).

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
INDEX_DIR = ROOT / "data"

# Everything Foundry Local writes (models, EPs, logs) lives here; override with LOCALRAG_HOME.
APP_DATA_DIR = os.environ.get("LOCALRAG_HOME", r"D:\localrag")
MODEL_CACHE_DIR = str(Path(APP_DATA_DIR) / "models")

# Catalog aliases; the SDK picks the best variant (NPU/GPU/CPU) for the device.
EMBED_ALIAS = "qwen3-embedding-0.6b"
# qwen3-8b was the most reliable on Turkish questions of the models I tried; use LOCALRAG_CHAT=qwen3-4b on smaller GPUs.
CHAT_ALIAS = os.environ.get("LOCALRAG_CHAT", "qwen3-8b")

# Chunk sizes are counted in words to avoid a tokenizer dependency.
CHUNK_WORDS = 130      # target chunk length
OVERLAP_WORDS = 25     # words shared between neighbouring chunks

# Retrieval
TOP_K = 4
# Scores I measured: relevant questions 0.50-0.65, unrelated ones 0.30-0.41.
MIN_SCORE = 0.45       # chunks below this are dropped; if none is left the model is skipped

# Qwen3-Embedding expects an instruction on the query side only.
QUERY_INSTRUCTION = (
    "Instruct: Given a question, retrieve the passages that answer it\n"
    "Query: "
)

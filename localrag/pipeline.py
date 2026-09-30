from dataclasses import dataclass
from typing import Iterator

from . import config, runtime
from .chunker import Chunk, chunk_document
from .loader import load_documents
from .store import VectorStore, fingerprint

# English instructions stick better with small models; the answer language is forced to Turkish.
SYSTEM_PROMPT = (
    "You answer questions using only the numbered sources below. Reply in Turkish, "
    "in 1-3 short sentences; technical terms may stay in English. After each claim, "
    "cite the source number like [1] or [2]. If the sources do not contain the answer, "
    "say you could not find it in the documents, but only if the sources really contain nothing related. "
    "Write the answer in your own words; do not repeat the question or copy the source text. "
    "Do not add facts that are not in the sources."
    "\n\nSources:\n{context}"
)
# Appended to the user message because the model drifts to English after a long context.
REMINDER = "\n\n(Türkçe, kısa ve kendi cümlelerinle cevapla; kaynak numarasını [n] olarak ekle.)"
# Qwen3 "thinks" first by default, which only adds latency here.
NO_THINK = " /no_think"


def strip_think(tokens: Iterator[str]) -> Iterator[str]:
    """Drop <think>...</think> blocks from a token stream."""
    buf, inside = "", False
    for tok in tokens:
        buf += tok
        while True:
            if inside:
                end = buf.find("</think>")
                if end == -1:
                    buf = buf[-8:]  # the closing tag may arrive split across tokens
                    break
                buf, inside = buf[end + 8:], False
            else:
                start = buf.find("<think>")
                if start == -1:
                    keep = len(buf) - 6  # an opening tag may arrive split across tokens
                    if keep > 0:
                        yield buf[:keep]
                        buf = buf[keep:]
                    break
                if start:
                    yield buf[:start]
                buf, inside = buf[start + 7:], True
    if not inside and buf:
        yield buf


def clean_stream(tokens: Iterator[str]) -> Iterator[str]:
    """Strip <think> blocks and leading blank lines (Qwen3 emits "\n\n" after an empty think block)."""
    started = False
    for tok in strip_think(tokens):
        if not started:
            tok = tok.lstrip()
            if not tok:
                continue
            started = True
        yield tok


@dataclass
class Source:
    n: int
    chunk: Chunk
    score: float

    @property
    def label(self) -> str:
        sec = f" › {self.chunk.section}" if self.chunk.section else ""
        return f"{self.chunk.source}{sec}"


class RagEngine:
    def __init__(self):
        print("Foundry Local başlatılıyor...")
        self.manager = runtime.start()
        runtime.register_hardware(self.manager)
        self.embed_model = runtime.load_model(self.manager, config.EMBED_ALIAS, "embedding modeli")
        self.chat_model = None
        self.embedder = self.embed_model.get_embedding_client()
        self.store: VectorStore | None = None

    # --- ingestion ---
    def ingest(self, force: bool = False) -> VectorStore:
        """Build or load the index; skips re-embedding when the docs haven't changed."""
        docs = load_documents(config.DOCS_DIR)
        if not docs:
            raise RuntimeError(f"{config.DOCS_DIR} içinde .txt/.md dosyası yok.")
        fp = fingerprint(docs)

        cached = None if force else VectorStore.load(config.INDEX_DIR)
        if cached and cached.fp == fp:
            self.store = cached
            print(f"Index güncel: {len(cached.chunks)} chunk ({len(docs)} doküman).")
            return cached

        chunks = [c for d in docs for c in chunk_document(d)]
        print(f"{len(docs)} doküman → {len(chunks)} chunk. Embedding üretiliyor...")
        # embed in batches of 16 to keep memory flat
        vectors: list[list[float]] = []
        for i in range(0, len(chunks), 16):
            batch = [c.text for c in chunks[i:i + 16]]
            resp = self.embedder.generate_embeddings(batch)
            vectors += [item.embedding for item in resp.data]
        self.store = VectorStore.build(vectors, chunks, fp)
        self.store.save(config.INDEX_DIR)
        print(f"Index kaydedildi: {config.INDEX_DIR}")
        return self.store

    # --- retrieval ---
    def retrieve(self, question: str, k: int = config.TOP_K) -> list[Source]:
        # the query gets the instruction prefix, documents don't
        q = self.embedder.generate_embedding(config.QUERY_INSTRUCTION + question)
        hits = self.store.search(q.data[0].embedding, k)
        return [Source(i + 1, c, s) for i, (c, s) in enumerate(hits)]

    # --- generation ---
    def _chat(self):
        # load the chat model lazily so ingest-only runs don't pay for it
        if self.chat_model is None:
            self.chat_model = runtime.load_model(
                self.manager, config.CHAT_ALIAS, "chat modeli",
                match_ep=runtime.provider_of(self.embed_model),
            )
            self.chat_client = self.chat_model.get_chat_client()
            self.chat_client.settings.temperature = 0.2
            self.chat_client.settings.max_tokens = 400
        return self.chat_client

    def preload_chat(self):
        self._chat()

    def answer(self, question: str) -> tuple[list[Source], Iterator[str]]:
        """Return (sources, token stream); the sources are known before the first token."""
        sources = self.retrieve(question)
        relevant = [s for s in sources if s.score >= config.MIN_SCORE]
        if not relevant:
            return [], iter(["Dokümanlarda bu soruyla ilgili bir bilgi bulamadım."])

        context = "\n\n".join(f"[{s.n}] ({s.label})\n{s.chunk.text}" for s in relevant)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
            {"role": "user", "content": question + REMINDER + (NO_THINK if "qwen3" in config.CHAT_ALIAS else "")},
        ]
        client = self._chat()

        def stream() -> Iterator[str]:
            for chunk in client.complete_streaming_chat(messages):
                text = chunk.choices[0].delta.content
                if text:
                    yield text

        return relevant, clean_stream(stream())

    def info(self) -> dict:
        """What the UI shows: which models are loaded and on which provider."""
        chat = self.chat_model
        return {
            "embedding": self.embed_model.id,
            "chat": chat.id if chat else None,
            "provider": runtime.provider_of(self.embed_model),
            "chunks": len(self.store.chunks) if self.store else 0,
            "docs": len({c.source for c in self.store.chunks}) if self.store else 0,
        }

    def close(self):
        for m in (self.chat_model, self.embed_model):
            if m is not None:
                try:
                    m.unload()
                except Exception:
                    pass

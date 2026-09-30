"""Tests for the parts that don't need a model. Run: python -m unittest"""
import tempfile
import unittest
from pathlib import Path

import numpy as np

from localrag.chunker import chunk_document
from localrag.config import OVERLAP_WORDS
from localrag.loader import Document, load_documents
from localrag.pipeline import clean_stream
from localrag.store import VectorStore

DOC = Document("a.md", "# Başlık Bir\n\n" + ("Bu bir cümledir. " * 60).strip()
               + "\n\n# Başlık İki\n\nKısa bir paragraf.")


class ChunkerTests(unittest.TestCase):
    def test_sections_do_not_mix(self):
        chunks = chunk_document(DOC)
        self.assertEqual(chunks[-1].section, "Başlık İki")
        self.assertNotIn("Kısa bir paragraf", " ".join(c.text for c in chunks[:-1]))

    def test_overlap_between_consecutive_chunks(self):
        first, second = [c for c in chunk_document(DOC) if c.section == "Başlık Bir"][:2]
        n = OVERLAP_WORDS
        self.assertEqual(second.text.split()[:n], first.text.split()[-n:])

    def test_no_empty_chunks(self):
        self.assertTrue(all(c.text.strip() for c in chunk_document(DOC)))


class StoreTests(unittest.TestCase):
    def test_cosine_ranking_and_roundtrip(self):
        chunks = chunk_document(DOC)[:3]
        vecs = [[1, 0], [0, 1], [1, 1]][: len(chunks)]
        store = VectorStore.build(vecs, chunks, "fp")
        top = store.search([1, 0.1], k=1)[0]
        self.assertIs(top[0], chunks[0])
        with tempfile.TemporaryDirectory() as d:
            store.save(Path(d))
            loaded = VectorStore.load(Path(d))
        self.assertEqual(loaded.fp, "fp")
        np.testing.assert_allclose(loaded.vectors, store.vectors)
        self.assertEqual(loaded.chunks[0].text, chunks[0].text)


class StreamTests(unittest.TestCase):
    def run_stream(self, parts):
        return "".join(clean_stream(iter(parts)))

    def test_think_block_and_leading_whitespace_removed(self):
        self.assertEqual(self.run_stream(["<think>", "\n\n", "</think>", "\n\n", "Merhaba"]), "Merhaba")

    def test_split_tags(self):
        self.assertEqual(self.run_stream(["Mer", "haba <thi", "nk>x</th", "ink> dünya"]), "Merhaba  dünya")

    def test_plain_text_untouched(self):
        self.assertEqual(self.run_stream(["a<b ", "c [1]."]), "a<b c [1].")


class LoaderTests(unittest.TestCase):
    def test_reads_only_txt_and_md(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "x.txt").write_text("merhaba", encoding="utf-8")
            (Path(d) / "y.md").write_text("# T\n\nmetin", encoding="utf-8")
            (Path(d) / "z.pdf").write_text("yok", encoding="utf-8")
            (Path(d) / "bos.txt").write_text("  ", encoding="utf-8")
            names = [x.name for x in load_documents(Path(d))]
        self.assertEqual(names, ["x.txt", "y.md"])


if __name__ == "__main__":
    unittest.main()

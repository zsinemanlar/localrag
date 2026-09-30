"""Small browser UI served with the standard library http.server.

Answers are streamed as newline-delimited JSON: sources first, then tokens.
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = Path(__file__).resolve().parent / "web" / "index.html"


def serve(engine, port: int = 8080) -> None:
    # native model calls run one request at a time
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep the console quiet
            pass

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/":
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/info":
                body = json.dumps(engine.info(), ensure_ascii=False).encode()
                self._send(200, body, "application/json; charset=utf-8")
            else:
                self._send(404, b"not found", "text/plain")

        def do_POST(self):
            if self.path != "/ask":
                return self._send(404, b"not found", "text/plain")
            length = int(self.headers.get("Content-Length", 0))
            question = json.loads(self.rfile.read(length) or b"{}").get("question", "").strip()
            if not question:
                return self._send(400, b"empty question", "text/plain")

            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            def emit(obj):
                self.wfile.write((json.dumps(obj, ensure_ascii=False) + "\n").encode())
                self.wfile.flush()

            with lock:
                t0 = time.perf_counter()
                sources, stream = engine.answer(question)
                emit({"type": "sources", "items": [
                    {"n": s.n, "file": s.chunk.source, "section": s.chunk.section,
                     "score": round(s.score, 3), "text": s.chunk.text} for s in sources]})
                first = None
                for token in stream:
                    if first is None:
                        first = time.perf_counter() - t0
                    emit({"type": "token", "text": token})
                emit({"type": "done", "first": first, "total": time.perf_counter() - t0})

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"\nlocalrag arayüzü: http://127.0.0.1:{port}  (durdurmak için Ctrl+C)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

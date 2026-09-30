"""Command line entry point.

    python app.py            # interactive Q&A
    python app.py ingest     # (re)build the index
    python app.py ask "..."  # ask one question and exit
    python app.py web        # browser UI
"""
import argparse
import os
import sys
import time

from localrag.pipeline import RagEngine

# enables ANSI colors in the Windows console
os.system("")
sys.stdout.reconfigure(encoding="utf-8")

DIM, BOLD, ACCENT, RESET = "\033[2m", "\033[1m", "\033[38;5;75m", "\033[0m"
if not sys.stdout.isatty():
    DIM = BOLD = ACCENT = RESET = ""


def print_sources(sources):
    if not sources:
        return
    print(f"\n{DIM}Kaynaklar{RESET}")
    for s in sources:
        print(f"{DIM}  [{s.n}] {s.label}  (benzerlik {s.score:.2f}){RESET}")


def ask_once(engine: RagEngine, question: str) -> None:
    t0 = time.perf_counter()
    sources, stream = engine.answer(question)
    print()
    first = None
    for token in stream:
        if first is None:
            first = time.perf_counter() - t0
        print(token, end="", flush=True)
    print()
    print_sources(sources)
    total = time.perf_counter() - t0
    if first is not None:
        print(f"{DIM}\n  ilk token {first:.1f}s · toplam {total:.1f}s · cihaz üzerinde, ağ isteği yok{RESET}")


def chat(engine: RagEngine) -> None:
    engine.preload_chat()
    print(f"\n{BOLD}localrag{RESET} {DIM}· Foundry Local ile tamamen yerel · çıkmak için 'q'{RESET}\n")
    while True:
        try:
            question = input(f"{ACCENT}?{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"q", "quit", "exit", "çık"}:
            break
        ask_once(engine, question)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(prog="localrag", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd")
    ing = sub.add_parser("ingest", help="docs/ klasörünü indexle")
    ing.add_argument("--force", action="store_true", help="index güncel olsa da yeniden üret")
    ask = sub.add_parser("ask", help="tek bir soru sor")
    ask.add_argument("question")
    web = sub.add_parser("web", help="tarayıcı arayüzü")
    web.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    engine = RagEngine()
    try:
        engine.ingest(force=getattr(args, "force", False))
        if args.cmd == "ingest":
            return
        if args.cmd == "ask":
            engine.preload_chat()
            ask_once(engine, args.question)
        elif args.cmd == "web":
            from web import serve
            engine.preload_chat()
            serve(engine, args.port)
        else:
            chat(engine)
    finally:
        engine.close()


if __name__ == "__main__":
    main()

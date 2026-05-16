from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

try:
    from .ingest import ingest_document
    from .rag import DEFAULT_MODEL, answer_query, retrieve_chunks, stream_answer_query
except ImportError:  # pragma: no cover - fallback for direct script execution
    from ingest import ingest_document
    from rag import DEFAULT_MODEL, answer_query, retrieve_chunks, stream_answer_query


console = Console()


@dataclass(slots=True)
class ChatState:
    model: str = DEFAULT_MODEL
    top_k: int = 3
    history: list[tuple[str, str]] = field(default_factory=list)


def print_banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]1337-RAG[/bold cyan]\n[dim]Chat over your Pinecone-backed notes[/dim]",
            border_style="cyan",
        )
    )


def print_help() -> None:
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_row("/help", "Show commands")
    table.add_row("/clear", "Clear the screen and reset session history")
    table.add_row("/reset", "Forget conversation history")
    table.add_row("/model <name>", "Set the Ollama model")
    table.add_row("/topk <n>", "Change how many chunks are retrieved")
    table.add_row("/context <question>", "Inspect retrieved chunks for a query")
    table.add_row("/ingest", "Re-index data/notes.txt")
    table.add_row("/exit", "Quit")
    console.print(Panel(table, title="Commands", border_style="blue"))


def render_context(question: str, top_k: int) -> None:
    chunks = retrieve_chunks(question, top_k=top_k)
    if not chunks:
        console.print("[yellow]No context retrieved.[/yellow]")
        return

    table = Table(title="Retrieved context", show_lines=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Score", style="magenta", width=10)
    table.add_column("Text", overflow="fold")

    for i, chunk in enumerate(chunks, start=1):
        score = "-" if chunk.score is None else f"{chunk.score:.3f}"
        table.add_row(str(i), score, chunk.text)

    console.print(table)


def handle_command(line: str, state: ChatState) -> bool:
    parts = line.strip().split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if command in {"/exit", "/quit"}:
        return False
    if command == "/help":
        print_help()
        return True
    if command == "/clear":
        console.clear()
        print_banner()
        return True
    if command == "/reset":
        state.history.clear()
        console.print("[green]Conversation reset.[/green]")
        return True
    if command == "/model":
        if not arg:
            console.print(f"[yellow]Current model:[/yellow] {state.model}")
        else:
            state.model = arg
            console.print(f"[green]Model set to[/green] {state.model}")
        return True
    if command == "/topk":
        if arg:
            try:
                state.top_k = max(1, int(arg))
                console.print(f"[green]top_k set to[/green] {state.top_k}")
            except ValueError:
                console.print("[red]top_k must be a number.[/red]")
        else:
            console.print(f"[yellow]Current top_k:[/yellow] {state.top_k}")
        return True
    if command == "/context":
        if not arg:
            console.print("[red]Provide a question after /context.[/red]")
        else:
            render_context(arg, state.top_k)
        return True
    if command == "/ingest":
        count = ingest_document(Path("data/notes.txt"))
        console.print(f"[green]Indexed[/green] {count} chunks.")
        return True

    console.print("[red]Unknown command. Type /help.[/red]")
    return True


def chat_loop(state: ChatState) -> None:
    print_banner()
    console.print("Type a question, or /help for commands.\n")

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]you[/bold cyan]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Bye.[/dim]")
            break

        if not user_input.strip():
            continue

        if user_input.startswith("/"):
            if not handle_command(user_input, state):
                break
            continue

        console.print("[bold green]assistant[/bold green]")
        stream, chunks = stream_answer_query(
            user_input,
            model=state.model,
            top_k=state.top_k,
        )

        console.print(Panel.fit(f"[dim]{len(chunks)} chunks retrieved[/dim]", border_style="green"))
        with console.status("Thinking...", spinner="dots"):
            response_parts = []
            for token in stream:
                response_parts.append(token)
                console.print(token, end="")

        console.print()
        response_text = "".join(response_parts).strip()
        state.history.append((user_input, response_text))


def one_shot(question: str, model: str, top_k: int) -> None:
    print_banner()
    response, chunks = answer_query(question, model=model, top_k=top_k)
    console.print(Panel.fit(f"[dim]{len(chunks)} chunks retrieved[/dim]", border_style="green"))
    console.print(response)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="1337-rag", description="Chat with your indexed notes.")
    parser.add_argument("question", nargs="?", help="Ask a single question and exit")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    parser.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")
    return parser


def main(argv: Iterable[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.question:
        one_shot(args.question, model=args.model, top_k=args.top_k)
        return

    chat_loop(ChatState(model=args.model, top_k=args.top_k))

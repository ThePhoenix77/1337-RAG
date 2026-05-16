from __future__ import annotations

from dataclasses import dataclass

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, RichLog, Static

try:
    from .rag import DEFAULT_MODEL, RetrievedChunk, answer_query, ensure_index_current
except ImportError:  # pragma: no cover - fallback for direct script execution
    from rag import DEFAULT_MODEL, RetrievedChunk, answer_query, ensure_index_current


@dataclass(slots=True)
class TuiConfig:
    model: str = DEFAULT_MODEL
    top_k: int = 3


class RagTui(App):
    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+l", "clear_log", "Clear chat"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    #body {
        height: 1fr;
    }

    #left {
        width: 2fr;
        height: 1fr;
    }

    #right {
        width: 1fr;
        height: 1fr;
    }

    #chat-log {
        height: 1fr;
        border: round $primary;
    }

    #query-input {
        width: 1fr;
    }

    #model-input {
        width: 22;
    }

    #topk-input {
        width: 8;
    }

    #apply-settings-btn {
        width: 10;
    }

    #send-btn {
        width: 10;
    }

    #status {
        height: auto;
        min-height: 3;
        border: round $accent;
        padding: 0 1;
    }

    #chunks-table {
        height: 1fr;
        border: round $secondary;
    }

    #chunk-content {
        height: 12;
        border: round $warning;
        padding: 0 1;
    }
    """

    def __init__(self, config: TuiConfig):
        super().__init__()
        self.config = config
        self.latest_chunks: list[RetrievedChunk] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="body"):
            with Vertical(id="left"):
                yield RichLog(id="chat-log", wrap=True, markup=True)
                with Horizontal():
                    yield Input(placeholder="Ask a question...", id="query-input")
                    yield Button("Send", id="send-btn", variant="primary")
            with Vertical(id="right"):
                with Horizontal():
                    yield Input(value=self.config.model, placeholder="Model", id="model-input")
                    yield Input(value=str(self.config.top_k), placeholder="top_k", id="topk-input")
                    yield Button("Apply", id="apply-settings-btn")
                yield Static("Ready", id="status")
                yield DataTable(id="chunks-table")
                yield Static("Click a retrieved chunk to view it.", id="chunk-content")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#chunks-table", DataTable)
        table.add_columns("#", "Score", "Snippet")
        table.cursor_type = "row"

        chat = self.query_one("#chat-log", RichLog)
        chat.write("[bold cyan]1337-RAG Clickable CLI[/bold cyan]")
        chat.write("Ask a question, then click any chunk on the right to inspect its content.")
        chat.write(f"Current settings -> model: [cyan]{self.config.model}[/cyan], top_k: [cyan]{self.config.top_k}[/cyan]")
        self._set_status(f"Ready - model={self.config.model}, top_k={self.config.top_k}")

    def action_clear_log(self) -> None:
        self.query_one("#chat-log", RichLog).clear()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send-btn":
            self._submit_question()
        elif event.button.id == "apply-settings-btn":
            self._apply_settings()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "query-input":
            self._submit_question()

    def _submit_question(self) -> None:
        input_widget = self.query_one("#query-input", Input)
        question = input_widget.value.strip()
        if not question:
            return

        input_widget.value = ""
        self._ask_and_render(question)

    def _apply_settings(self) -> None:
        chat = self.query_one("#chat-log", RichLog)
        model_input = self.query_one("#model-input", Input)
        topk_input = self.query_one("#topk-input", Input)

        model = model_input.value.strip() or self.config.model

        try:
            top_k = int(topk_input.value.strip())
            if top_k < 1:
                raise ValueError
        except ValueError:
            self._set_status("Invalid top_k (must be >= 1)")
            chat.write("[bold red]error:[/bold red] top_k must be a positive integer")
            return

        self.config.model = model
        self.config.top_k = top_k
        self._set_status(f"Updated - model={self.config.model}, top_k={self.config.top_k}")
        chat.write(f"[green]settings updated[/green] -> model: [cyan]{model}[/cyan], top_k: [cyan]{top_k}[/cyan]")

    def _set_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)

    def _ask_and_render(self, question: str) -> None:
        chat = self.query_one("#chat-log", RichLog)
        table = self.query_one("#chunks-table", DataTable)
        content = self.query_one("#chunk-content", Static)

        chat.write(f"[bold cyan]you:[/bold cyan] {question}")
        self._set_status("Checking for notes updates...")

        try:
            reindexed = ensure_index_current()
            if reindexed:
                chat.write("[yellow]notes.txt changed - re-indexed[/yellow]")

            self._set_status("Retrieving and generating answer...")
            answer, chunks = answer_query(
                question,
                model=self.config.model,
                top_k=self.config.top_k,
                check_updates=False,
            )
        except Exception as exc:
            chat.write(f"[bold red]error:[/bold red] {exc}")
            self._set_status("Error")
            return

        chat.write(f"[bold green]assistant:[/bold green] {answer}")
        self._set_status(f"Done - {len(chunks)} chunks retrieved")

        self.latest_chunks = chunks
        table.clear()

        if not chunks:
            content.update("No chunks retrieved for this query.")
            return

        for i, chunk in enumerate(chunks, start=1):
            snippet = chunk.text.replace("\n", " ").strip()
            if len(snippet) > 120:
                snippet = f"{snippet[:117]}..."
            score = "-" if chunk.score is None else f"{chunk.score:.3f}"
            table.add_row(str(i), score, snippet)

        content.update(chunks[0].text)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if not self.latest_chunks:
            return

        try:
            row_index = event.cursor_row
            selected = self.latest_chunks[row_index]
        except (IndexError, TypeError):
            return

        self.query_one("#chunk-content", Static).update(selected.text)


def run_tui(model: str = DEFAULT_MODEL, top_k: int = 3) -> None:
    RagTui(TuiConfig(model=model, top_k=top_k)).run()

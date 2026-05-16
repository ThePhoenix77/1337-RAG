# 1337-RAG

A RAG system answering the 1337 school about questions, with both an interactive CLI and also a TUI for easier use.

## Run

```bash
python main.py
```

Ask your 1337 related question:

```text
"What is 1337 school?"
```
```text
"How does the 1337 school work?"
```
```text
"Tell me more about the 1337 school campuses?"
```

To use the CLI mode if you want:

```bash
python main.py --classic
```
Useful commands inside the chat:

- /help
- /model mistral
- /topk 5
- /context your question here
- /ingest
- /reset
- /exit

## N.B
If you're interested about RAG systems and how they work under the hood, check my latest article [RAG - Complete Practical Guide](https://tahaboussaden.me/blog/rag-complete-practical-guide).

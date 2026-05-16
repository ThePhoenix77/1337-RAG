# 1337-RAG

Interactive CLI for chatting with your indexed notes using Ollama + Pinecone.

The default mode is now a clickable terminal UI:
- click the retrieved chunks table rows to inspect full chunk content
- type your question in the input bar and press Enter
- change `model` and `top_k` live from the right panel, then click `Apply`

## Run

```bash
python main.py
```

Ask a one-off question:

```bash
python main.py "What is retrieval augmented generation?"
```

Useful commands inside the chat:

- /help
- /model mistral
- /topk 5
- /context your question here
- /ingest
- /reset
- /exit

Use old CLI mode if needed:

```bash
python main.py --classic
```
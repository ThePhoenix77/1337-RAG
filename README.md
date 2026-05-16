# 1337-RAG

A RAG system that answers questions about 1337 School, with both a clickable TUI and a classic CLI.

## Quick setup

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the Python dependencies:

```bash
pip install -r requirements.txt
```

3. Add your Pinecone API key in a `.env` file:

```bash
PINECONE_API_KEY=your_api_key_here
```

4. Install Ollama and pull the Mistral model:

```bash
ollama pull mistral
```

## Usage

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

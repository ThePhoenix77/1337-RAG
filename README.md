# 1337-RAG

A sophisticated Retrieval-Augmented Generation (RAG) system designed to answer questions about 1337 Coding School Morocco. This project demonstrates a complete RAG workflow with both a modern clickable Textual User Interface (TUI) and a classic Command Line Interface (CLI).

## Features

- **Dual Interface Modes**: Choose between a modern clickable TUI or traditional CLI
- **Vector Database Integration**: Uses Pinecone for efficient similarity search and retrieval
- **Local LLM Processing**: Powered by Ollama for embeddings and text generation
- **Automatic Re-indexing**: Smart file change detection ensures your knowledge base stays current
- **Streaming Responses**: Real-time token streaming for interactive conversations
- **Context Inspection**: View retrieved chunks to understand the RAG process
- **Configurable Parameters**: Adjust model selection and retrieval parameters on the fly
- **Conversation History**: Maintain context across multiple queries in CLI mode

## Architecture

The system follows a complete RAG pipeline:

1. **Document Ingestion**: Raw text is chunked into overlapping segments
2. **Embedding Generation**: Each chunk is converted to a vector representation
3. **Vector Storage**: Embeddings are stored in Pinecone for similarity search
4. **Query Processing**: User questions are embedded and matched against stored chunks
5. **Context Assembly**: Retrieved chunks are combined into a context prompt
6. **Response Generation**: Local LLM generates answers using the retrieved context

### Project Structure

```
1337-RAG/
├── app/
│   ├── __init__.py
│   ├── chunking.py          # Text chunking with overlap strategy
│   ├── cli.py               # Classic CLI interface implementation
│   ├── embeddings.py        # Ollama embedding generation
│   ├── file_tracker.py      # File change detection for auto-reindexing
│   ├── ingest.py            # Document ingestion and vector storage
│   ├── pinecone_service.py  # Pinecone index management
│   ├── rag.py               # Core RAG logic (query answering, retrieval)
│   └── tui.py               # Textual-based clickable interface
├── data/
│   └── notes.txt            # Source knowledge base about 1337 School
├── .cache/                  # File hash cache for change detection
├── .env                     # Environment variables (API keys)
├── .gitignore
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Setup

### Prerequisites

- Python 3.8 or higher
- Pinecone API account
- Ollama installed locally

### Installation Steps

1. **Clone the repository** (if not already done):
```bash
git clone <repository-url>
cd 1337-RAG
```

2. **Create and activate a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the project root:
```bash
PINECONE_API_KEY=your_pinecone_api_key_here
```

5. **Install and configure Ollama**:
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai

# Pull the required models
ollama pull mistral           # For text generation
ollama pull nomic-embed-text  # For embeddings
```

## Usage

### Starting the Application

**Default TUI Mode (Recommended)**:
```bash
python main.py
```

**Classic CLI Mode**:
```bash
python main.py --classic
```

**One-shot Question**:
```bash
python main.py "What is 1337 school?"
```

**Custom Parameters**:
```bash
python main.py --model llama2 --top-k 5
```

### TUI Interface Features

The modern TUI provides an interactive experience with:

- **Left Panel**: Chat interface for questions and answers
- **Right Panel**: Retrieved chunks display with click-to-view functionality
- **Settings Bar**: Configure model and top_k parameters in real-time
- **Status Updates**: Real-time feedback on indexing and processing
- **Keyboard Shortcuts**: 
  - `Ctrl+C`: Quit application
  - `Ctrl+L`: Clear chat log

### CLI Commands

In classic CLI mode, use these commands:

- `/help` - Display available commands
- `/clear` - Clear screen and reset session
- `/reset` - Forget conversation history
- `/model <name>` - Set the Ollama model (e.g., `/model llama2`)
- `/topk <n>` - Change number of chunks retrieved (e.g., `/topk 5`)
- `/context <question>` - Inspect retrieved chunks for a query
- `/ingest` - Manually re-index data/notes.txt
- `/exit` - Quit the application

### Example Questions

Try these questions about 1337 Coding School:

```
"What is 1337 school?"
"How does the 1337 school work?"
"Tell me more about the 1337 school campuses?"
"What is the admission process for 1337?"
"Explain the pedagogical approach used at 1337"
"What technologies are taught in the curriculum?"
```

## Technical Workflow

### 1. Document Ingestion Pipeline

The ingestion process (`app/ingest.py`) handles the initial knowledge base setup:

```python
# Process:
1. Read source document (data/notes.txt)
2. Chunk text into overlapping segments (300 chars, 50 overlap)
3. Generate embeddings for each chunk using Ollama
4. Upload vectors to Pinecone with metadata
5. Cache file hash for change detection
```

### 2. Chunking Strategy

The system uses a sliding window approach (`app/chunking.py`):

- **Chunk Size**: 300 characters
- **Overlap**: 50 characters
- **Purpose**: Maintains context continuity between chunks

### 3. Embedding Generation

Embeddings are generated locally using Ollama (`app/embeddings.py`):

- **Model**: `nomic-embed-text`
- **Dimension**: 768 (matches Pinecone index configuration)
- **Process**: Text → Ollama API → Vector representation

### 4. Vector Database Management

Pinecone service (`app/pinecone_service.py`) handles:

- **Index Creation**: Automatic index creation if not exists
- **Configuration**: 
  - Dimension: 768 (for nomic-embed-text)
  - Metric: Cosine similarity
  - Deployment: Serverless on AWS us-east-1
- **Operations**: Upsert vectors, query by similarity

### 5. Query Processing Pipeline

When a user asks a question (`app/rag.py`):

```python
# Query Flow:
1. Check if source file changed → Re-index if needed
2. Generate embedding for user query
3. Retrieve top-k similar chunks from Pinecone
4. Build context from retrieved chunks
5. Construct prompt with context and question
6. Stream response from Ollama LLM
7. Display answer with chunk count
```

### 6. File Change Detection

Smart caching system (`app/file_tracker.py`):

- **Hash Computation**: SHA256 of source file
- **Cache Storage**: `.cache/{filename}.hash`
- **Change Detection**: Compare current vs cached hash
- **Auto Re-indexing**: Trigger re-ingestion when changes detected

### 7. Response Generation

The system uses a carefully designed prompt (`app/rag.py`):

```
You are a helpful AI assistant.
Answer the question ONLY using the provided context.
If the answer is not found in the context, say "I don't know."

Context: {retrieved_chunks}

Question: {user_query}

Answer:
```

## Configuration

### Environment Variables

- `PINECONE_API_KEY`: Your Pinecone API key (required)

### Default Parameters

- **Model**: `mistral` (Ollama)
- **Top-K**: 3 (number of chunks to retrieve)
- **Chunk Size**: 300 characters
- **Overlap**: 50 characters
- **Embedding Model**: `nomic-embed-text`

### Customization

You can modify these defaults in `app/rag.py`:

```python
DEFAULT_MODEL = "mistral"
DEFAULT_TOP_K = 3
DEFAULT_DOC_PATH = "data/notes.txt"
```

## Development

### Adding New Documents

To add new knowledge:

1. Place your document in the `data/` directory
2. Update `DEFAULT_DOC_PATH` in `app/rag.py` if needed
3. Run the application with `/ingest` command or let auto-detection handle it

### Modifying Chunking Strategy

Edit `app/chunking.py` to adjust:

```python
def chunk_text(text, chunk_size=300, overlap=50):
    # Adjust parameters based on your needs
```

### Changing Embedding Model

Update `app/embeddings.py` and `app/pinecone_service.py`:

```python
# In embeddings.py
response = ollama.embeddings(model="your-model", prompt=text)

# In pinecone_service.py  
pc.create_index(dimension=your_model_dimension, ...)
```

## Troubleshooting

### Common Issues

**Pinecone Connection Error**:
- Verify your API key in `.env`
- Check your Pinecone account status
- Ensure you have available indexes

**Ollama Model Not Found**:
- Run `ollama pull mistral` and `ollama pull nomic-embed-text`
- Verify Ollama is running: `ollama serve`

**Import Errors**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**No Context Retrieved**:
- Check if document is indexed: use `/ingest` command
- Verify Pinecone index has data
- Try increasing `top_k` parameter

## License

MIT License. See `LICENSE` for details.


## Learning Resources

If you're interested in RAG systems and how they work under the hood, check out this comprehensive guide:

[RAG - Complete Practical Guide](https://tahaboussaden.me/blog/rag-complete-practical-guide)

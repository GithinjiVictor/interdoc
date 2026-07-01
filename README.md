# 📄 InterDoc — Ask Questions to Your Documents

InterDoc is a **document intelligence API** that lets you upload files (PDFs or plain text) and then ask questions about them in plain English. It reads your documents, breaks them into pieces, stores them intelligently, and uses an LLM (Llama 3.3 via Groq) to give you accurate, sourced answers — without hallucinating content that isn't there.

Think of it as a private, API-powered chatbot that only knows what *you* give it.

---

## 🧠 How It Works (Plain English)

When you upload a document, three things happen behind the scenes:

1. **Text Extraction** — The file is read. If it's a PDF, each page's text is pulled out. If it's a plain `.txt` file, it's decoded directly.

2. **Chunking** — The full text is split into overlapping "chunks" of ~300 words each. The overlap (50 words) ensures that answers don't get cut off at a boundary between two chunks.

3. **Embedding & Storage** — Each chunk is converted into a vector (a list of numbers that captures its *meaning*) using a local AI model (`all-MiniLM-L6-v2`). These vectors are saved to a local database (ChromaDB) so they persist even after the server restarts.

When you ask a question:

1. Your question is also converted into a vector.
2. ChromaDB finds the chunks whose meaning is closest to your question (semantic search, not just keyword matching).
3. Those chunks are assembled into a prompt and sent to **Llama 3.3 70B** (via Groq's API).
4. The LLM answers using *only* those chunks — it won't guess or make things up. If the answer isn't in your documents, it says so.

---

## 📁 Project Structure

```
interdoc/
│
├── app/                        # All application code lives here
│   ├── main.py                 # FastAPI app — defines the API endpoints
│   ├── ingestion.py            # Reads files and splits text into chunks
│   ├── vectorstore.py          # Stores and searches chunks using ChromaDB
│   ├── rag.py                  # Builds the prompt and calls the Groq LLM
│   ├── .env                    # Your secret API key (never commit this!)
│   └── venv/                   # Python virtual environment
│
└── README.md                   # You are here
```

---

## ⚙️ Setup

### 1. Prerequisites

- Python 3.10 or newer
- A free [Groq API key](https://console.groq.com/) — it's fast and free to sign up

### 2. Clone & enter the project

```bash
git clone <your-repo-url>
cd interdoc
```

### 3. Create and activate a virtual environment

```bash
python -m venv app/venv

# On Windows (Git Bash / MINGW):
source app/venv/Scripts/activate

# On Windows (PowerShell):
app\venv\Scripts\Activate.ps1

# On macOS / Linux:
source app/venv/bin/activate
```

### 4. Install dependencies

```bash
pip install fastapi uvicorn pypdf chromadb sentence-transformers groq python-dotenv
```

### 5. Add your Groq API key

Open `app/.env` and paste your key:

```
GROQ_API_KEY=your_key_here
```

> 💡 Get your key at [console.groq.com](https://console.groq.com/). It's free and takes about 30 seconds.

---

## 🚀 Running the Server

> **Important:** Always run this command from the **project root** (`interdoc/`), not from inside the `app/` folder.

```bash
# Make sure you're in the right place:
cd /path/to/interdoc

uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process ...
```

The `--reload` flag means the server automatically restarts whenever you edit a file — very handy during development.

---

## 📡 API Endpoints

### `GET /`
Health check. Confirms the server is running.

**Response:**
```json
{ "status": "alive" }
```

---

### `POST /upload`
Upload a document (PDF or `.txt`). The file is processed and stored automatically.

**Request:** `multipart/form-data` with a `file` field.

**Example with curl:**
```bash
curl -X POST http://127.0.0.1:8000/upload \
  -F "file=@path/to/your/document.pdf"
```

**Response:**
```json
{
  "filename": "document.pdf",
  "chunks_created": 42
}
```

---

### `POST /query`
Ask a question about your uploaded documents.

**Request body (JSON):**
```json
{
  "question": "What are the main conclusions of the report?",
  "top_k": 4
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `question` | string | required | The question you want answered |
| `top_k` | integer | `4` | How many document chunks to use as context |

**Example with curl:**
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the refund policy?", "top_k": 4}'
```

**Response:**
```json
{
  "answer": "According to [Source 1], the refund policy allows returns within 30 days of purchase...",
  "sources": [
    { "sources": "policy.pdf", "chunk_index": 3 },
    { "sources": "policy.pdf", "chunk_index": 4 }
  ]
}
```

> 💡 You can also explore all endpoints interactively via the auto-generated docs at **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** once the server is running.

---

## 🔒 A Note on the API Key

Your `app/.env` file contains a real secret key. Make sure it is **never committed to Git**. Add it to your `.gitignore`:

```
app/.env
app/venv/
data/
```

---

## 🛠 Tech Stack

| Tool | What it does |
|------|-------------|
| **FastAPI** | Web framework — handles HTTP requests |
| **pypdf** | Extracts text from PDF files |
| **ChromaDB** | Local vector database — stores and searches chunks |
| **sentence-transformers** | Converts text into semantic vectors locally |
| **Groq + Llama 3.3 70B** | The LLM that reads chunks and generates answers |
| **python-dotenv** | Loads the API key from the `.env` file |

---

## 💡 Tips

- **Multiple documents** — You can upload as many files as you want. All of them go into the same vector store and will be searched together.
- **Persistent storage** — ChromaDB saves data to `./data/chroma_db/`. Your documents survive server restarts.
- **Honest answers** — The LLM is instructed not to guess. If the answer isn't in your documents, it will tell you so rather than making something up.
- **Supported formats** — Currently `.pdf` and plain text files (`.txt`, `.md`, etc.). Other formats can be added to `ingestion.py`.

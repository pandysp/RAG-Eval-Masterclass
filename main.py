from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    PromptTemplate,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
import os
import sys

# Load API key from external file
config_path = "./openai_key.env"
load_dotenv(dotenv_path=config_path)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your_api_key_here":
    print("ERROR: OPENAI_API_KEY is not set or still the placeholder.")
    print("Please set your key in openai_key.env")
    sys.exit(1)
os.environ["OPENAI_API_KEY"] = api_key

# Models
Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Chunking (512 tokens, 50 overlap — LlamaIndex defaults)
Settings.chunk_size = 512
Settings.chunk_overlap = 50

# Data directory
directory_path = "./data"
file_metadata = lambda x: {"filename": x}
os.makedirs("data", exist_ok=True)

# Build or load the vector index
PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    reader = SimpleDirectoryReader(directory_path, file_metadata=file_metadata)
    documents = reader.load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)


# ---------------------------------------------------------------------------
# Prompts — switch between baseline and improved to see how evals change
# ---------------------------------------------------------------------------

PROMPT_BASELINE = PromptTemplate(
    "Beantworte die Frage basierend auf dem bereitgestellten Kontext.\n"
    "\n"
    "Kontext:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Frage: {query_str}\n"
    "Antwort: "
)

PROMPT_IMPROVED = PromptTemplate(
    "Du bist ein hilfreicher Assistent fuer CloudBase. "
    "Beantworte die Frage ausschliesslich anhand des bereitgestellten Kontexts.\n"
    "\n"
    "Regeln:\n"
    "- Antworte immer auf Deutsch.\n"
    "- Wenn der Kontext die Antwort nicht enthaelt, sage klar: "
    '"Dazu liegen mir keine Informationen vor."\n'
    "- Erfinde niemals Informationen, die nicht im Kontext stehen.\n"
    "- Nenne alle relevanten Zahlen, Preise, Daten, Fristen und "
    "Status-Angaben (z.B. Beta) vollstaendig.\n"
    "- Wenn eine Einschraenkung existiert, erklaere auch, wer die "
    "Berechtigung stattdessen hat.\n"
    "\n"
    "Kontext:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Frage: {query_str}\n"
    "Antwort: "
)

# >>> Change this line to switch prompts <<<
SYSTEM_PROMPT = PROMPT_BASELINE


# Query engine
query_engine = index.as_query_engine(
    response_mode="tree_summarize",
    summary_template=SYSTEM_PROMPT,
)


def update_query_engine(index):
    global query_engine
    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        summary_template=SYSTEM_PROMPT,
    )


app = FastAPI()

SUPPORTED_EXTENSIONS = (".txt", ".pdf", ".md")


def filter_file_format(files: list[UploadFile]) -> tuple:
    filtered = [f for f in files if f.filename.endswith(SUPPORTED_EXTENSIONS)]
    removed = [f.filename for f in files if not f.filename.endswith(SUPPORTED_EXTENSIONS)]
    return removed, filtered


@app.post("/ingest")
async def ingest(
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    if len(files) == 1 and files[0].filename == "":
        return JSONResponse(
            status_code=400,
            content={"message": "No files detected. Please upload at least one file."},
        )

    removed_documents, files = filter_file_format(files)
    new_documents = []

    if files:
        for file in files:
            out_file_path = os.path.join("data", file.filename)
            try:
                with open(out_file_path, "wb") as out_file:
                    while True:
                        chunk = await file.read(1024 * 1024)
                        if not chunk:
                            break
                        out_file.write(chunk)
                new_documents.append(out_file_path)
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"message": f"Failed to process file {file.filename}: {e}"},
                )

        try:
            reader = SimpleDirectoryReader(directory_path, file_metadata=file_metadata)
            documents = reader.load_data()
            for d in documents:
                index.insert(document=d)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": f"Failed to store file in index: {e}"},
            )

        try:
            index.storage_context.persist()
            update_query_engine(index)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": f"Failed to update index and query engine: {e}"},
            )

        try:
            for temp_file_path in new_documents:
                os.unlink(temp_file_path)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": f"Failed to clean up temp files: {e}"},
            )

    lines = []
    if removed_documents:
        lines.append("Removed (unsupported format): " + ", ".join(removed_documents))
    if new_documents:
        lines.append("Uploaded: " + ", ".join(os.path.basename(d) for d in new_documents))
    return {"message": "\n".join(lines) or "No files processed."}


@app.get("/query")
async def search_query(query: str):
    if not query.strip():
        return JSONResponse(
            status_code=400,
            content={"message": "No query text detected."},
        )
    try:
        response = query_engine.query(query)
        return {"query": query, "results": str(response)}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Failed to process query: {e}"},
        )


@app.get("/query_with_context")
async def query_with_context(query: str):
    """Query endpoint that returns both the answer and source documents for evaluation."""
    if not query.strip():
        return JSONResponse(
            status_code=400,
            content={"message": "No query text detected."},
        )
    try:
        response = query_engine.query(query)

        sources = []
        for node in getattr(response, "source_nodes", []):
            metadata = getattr(node.node, "metadata", {}) or {}
            source_info = {
                "text": getattr(node.node, "text", ""),
                "score": getattr(node, "score", None),
                "filename": metadata.get("filename", ""),
                "metadata": metadata,
            }
            sources.append(source_info)

        return {
            "query": query,
            "answer": str(response),
            "sources": sources,
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Failed to process query: {e}"},
        )


def load_content():
    try:
        with open("chat_interface.html", "r") as file:
            return file.read()
    except OSError as e:
        print(f"Error reading file: {e}")
        return "<html><body><h1>Error: chat_interface.html not found</h1></body></html>"


@app.get("/")
async def main():
    content = load_content()
    return HTMLResponse(content=content)

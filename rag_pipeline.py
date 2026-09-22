"""
rag_pipeline.py

Core Retrieval-Augmented Generation (RAG) logic for the AI Document Q&A Assistant.

Responsibilities:
- Load one or more documents (PDF or plain text)
- Split them into overlapping chunks, tagged by source file
- Embed the chunks using a free HuggingFace sentence-transformer model
- Build one FAISS index per source file (not one merged index)
- At query time, retrieve from every document individually and merge,
  so an answer that depends on facts from multiple files can't be
  starved out by one file dominating a single combined similarity search
- Call the Groq LLM directly with a capped, assembled context

Why per-file indices instead of one merged index:
A single shared index ranks every chunk from every file against each other
purely by similarity. If two documents are worded similarly (e.g. two resumes
both with an "Education" section), the top-k results can end up dominated by
just one or two files, and a third file's matching section is silently
dropped from the model's context - not because it wasn't relevant, but
because it never made it into the prompt. Retrieving a fixed number of
chunks per file guarantees every uploaded document gets a fair chance to
contribute, at a small, predictable, capped cost (see CHUNKS_PER_SOURCE below).
"""

import os
import tempfile
from collections import defaultdict

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Chunk size and overlap are intentionally generous: a heading (e.g. "SUMMARY")
# and the paragraph that follows it should end up in the same chunk whenever
# possible, so a semantic match on the heading also surfaces the content.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 250

GROQ_MODEL = "openai/gpt-oss-120b"
MAX_FILES = 5

# How many chunks to pull from EACH source document per question.
# Total context sent to the LLM is capped at MAX_FILES * CHUNKS_PER_SOURCE
# (5 * 3 = 15 chunks worst case), regardless of how many files are active.
# This keeps the prompt - and therefore the Groq API token cost - bounded
# and predictable, while still guaranteeing every document is represented.
CHUNKS_PER_SOURCE = 3

QA_PROMPT_TEMPLATE = """You are a helpful assistant answering questions using ONLY the context below,
which was retrieved from one or more documents the user uploaded. Each excerpt is
labeled with the file it came from.

If the answer cannot be found in the context, say clearly that the documents do not
contain that information. Do not make anything up. When relevant, mention which
document(s) an answer came from.

Context:
{context}

Question: {question}

Answer:"""

# Cache the embedding model at module level so it's only loaded once per process
_embeddings_cache = None


def get_embeddings():
    """Load (and cache) the HuggingFace embedding model."""
    global _embeddings_cache
    if _embeddings_cache is None:
        _embeddings_cache = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return _embeddings_cache


def load_document(uploaded_file):
    """
    Save a Streamlit UploadedFile to a temp path and load it into LangChain
    Document objects, based on its extension (.pdf or .txt). Tags every
    resulting Document with a 'source_file' metadata field so chunks can be
    traced back to the file they came from.
    """
    suffix = os.path.splitext(uploaded_file.name)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(tmp_path)
        elif suffix in (".txt", ".md"):
            loader = TextLoader(tmp_path, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file type: {suffix}. Please upload a PDF or .txt file.")

        documents = loader.load()
    finally:
        os.remove(tmp_path)

    if not documents or all(not d.page_content.strip() for d in documents):
        raise ValueError(
            f"No extractable text was found in '{uploaded_file.name}'. "
            "If it's a scanned/image-only PDF, OCR is not supported in this version."
        )

    for doc in documents:
        doc.metadata["source_file"] = uploaded_file.name

    return documents


def load_documents(uploaded_files):
    """
    Load multiple uploaded files (up to MAX_FILES) into a single combined
    list of LangChain Document objects, each tagged with its source filename.
    Raises a ValueError naming the offending file if one fails to load.
    """
    if len(uploaded_files) > MAX_FILES:
        raise ValueError(f"Please upload at most {MAX_FILES} files (you provided {len(uploaded_files)}).")

    all_documents = []
    for uploaded_file in uploaded_files:
        try:
            all_documents.extend(load_document(uploaded_file))
        except ValueError as e:
            raise ValueError(f"'{uploaded_file.name}': {e}")

    return all_documents


def build_vectorstores(documents):
    """
    Split documents into chunks and build one FAISS index PER SOURCE FILE
    (grouped by the 'source_file' metadata tag), sharing a single embeddings
    model instance across all of them.

    Returns (vectorstores, total_chunk_count) where vectorstores is a dict
    of {filename: FAISS index}.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Documents produced no text chunks to index.")

    chunks_by_source = defaultdict(list)
    for chunk in chunks:
        source = chunk.metadata.get("source_file", "unknown")
        chunks_by_source[source].append(chunk)

    embeddings = get_embeddings()
    vectorstores = {
        source: FAISS.from_documents(source_chunks, embeddings)
        for source, source_chunks in chunks_by_source.items()
    }
    return vectorstores, len(chunks)


def build_llm(groq_api_key: str):
    """Build the Groq-backed chat model used for answer generation."""
    if not groq_api_key:
        raise ValueError("Missing Groq API key. Set GROQ_API_KEY in your environment or Streamlit secrets.")

    return ChatGroq(
        model=GROQ_MODEL,
        api_key=groq_api_key,
        temperature=0.1,
    )


def retrieve_context(vectorstores: dict, question: str, k_per_source: int = CHUNKS_PER_SOURCE):
    """
    Run a similarity search against EVERY document's index independently and
    merge the results, so each uploaded file gets a guaranteed slice of the
    retrieved context instead of competing in one shared ranking.

    Returns a list of (document, score) tuples, sorted by relevance
    (lower score = closer match, per FAISS's L2 distance convention).
    """
    all_results = []
    for source, vectorstore in vectorstores.items():
        results = vectorstore.similarity_search_with_score(question, k=k_per_source)
        all_results.extend(results)

    all_results.sort(key=lambda pair: pair[1])
    return all_results


def format_source_label(doc, index):
    """Build a human-readable label for a retrieved source chunk, e.g.
    'Excerpt 1 - report.pdf (page 3)'."""
    label = f"Excerpt {index}"
    source_file = doc.metadata.get("source_file")
    if source_file:
        label += f" - {source_file}"
    page = doc.metadata.get("page")
    if page is not None:
        label += f" (page {page + 1})"
    return label


def answer_question(llm, vectorstores: dict, question: str):
    """
    Retrieve context per-source, assemble a capped prompt, and call the
    Groq LLM directly. Returns (answer_text, list_of_source_documents).
    """
    scored_docs = retrieve_context(vectorstores, question)
    source_docs = [doc for doc, _score in scored_docs]

    context_blocks = []
    for doc in source_docs:
        source_file = doc.metadata.get("source_file", "document")
        context_blocks.append(f"[From: {source_file}]\n{doc.page_content}")
    context_text = "\n\n---\n\n".join(context_blocks)

    prompt = QA_PROMPT_TEMPLATE.format(context=context_text, question=question)
    response = llm.invoke([HumanMessage(content=prompt)])
    answer = (response.content or "").strip()

    return answer, source_docs

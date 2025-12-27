from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from pathlib import Path
import tiktoken
from pypdf import PdfReader
from nltk.tokenize import sent_tokenize
import nltk
import json
from openai import OpenAI
import re

# Download nltk data if not already present
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs once on startup and once on shutdown.
    """
    global mongo_client

    # 🔹 Startup logic
    mongo_client = AsyncIOMotorClient(MONGODB_URL)
    app.state.mongo_client = mongo_client  # recommended over globals
    print(f"✅ Connected to MongoDB at {MONGODB_URL}")

    yield  # 🚀 App is running here

    # 🔹 Shutdown logic
    if mongo_client:
        mongo_client.close()
        print("🛑 MongoDB connection closed")


# Initialize FastAPI with lifespan
app = FastAPI(
    title="Long Document Analyzer System - Agentic Retrieval",
    lifespan=lifespan
)



# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "legal_rag_db"
COLLECTION_NAME = "documents"

load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not set. Please set it as environment variable.")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# File storage configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# MongoDB client
mongo_client: Optional[AsyncIOMotorClient] = None

# Global tokenizer name
TOKENIZER_NAME = "o200k_base"
DEFAULT_ROUTING_PREVIEW_TOKENS = 900

# Pydantic models
class QuestionRequest(BaseModel):
    document_id: str
    question: str
    max_depth: int = 2

class AnswerResponse(BaseModel):
    answer: str
    citations: List[str]
    scratchpad: str

class DocumentResponse(BaseModel):
    id: str
    filename: str
    upload_date: str
    file_path: str
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    token_count: Optional[int] = None



# Helper function to get database
def get_database():
    return mongo_client[DATABASE_NAME]

# Document processing functions (adapted from main.py)
def load_document_from_file(file_path: str, max_page: Optional[int] = None) -> Dict[str, Any]:
    """Load a document from a file path and return its text content with metadata."""
    print(f"Loading document from {file_path}...")
    
    with open(file_path, 'rb') as f:
        pdf_reader = PdfReader(f)
        
        full_text = ""
        page_count = len(pdf_reader.pages)
        
        # Apply page limit if specified
        max_page = max_page if max_page else page_count
        
        for i, page in enumerate(pdf_reader.pages):
            if i >= max_page:
                break
            full_text += page.extract_text() + "\n"
        
        # Count words and tokens
        word_count = len(re.findall(r'\b\w+\b', full_text))
        
        tokenizer = tiktoken.get_encoding(TOKENIZER_NAME)
        token_count = len(tokenizer.encode(full_text))
        
        print(f"Document loaded: {page_count} pages, {word_count} words, {token_count} tokens")
        
        return {
            "text": full_text,
            "page_count": page_count,
            "word_count": word_count,
            "token_count": token_count
        }

def split_into_20_chunks(text: str, min_tokens: int = 500) -> List[Dict[str, Any]]:
    """Split text into up to 20 chunks, respecting sentence boundaries."""
    sentences = sent_tokenize(text)
    tokenizer = tiktoken.get_encoding(TOKENIZER_NAME)
    
    chunks = []
    current_chunk_sentences = []
    current_chunk_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = len(tokenizer.encode(sentence))
        
        if (current_chunk_tokens + sentence_tokens > min_tokens * 2) and current_chunk_tokens >= min_tokens:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append({
                "id": len(chunks),
                "text": chunk_text
            })
            current_chunk_sentences = [sentence]
            current_chunk_tokens = sentence_tokens
        else:
            current_chunk_sentences.append(sentence)
            current_chunk_tokens += sentence_tokens
    
    if current_chunk_sentences:
        chunk_text = " ".join(current_chunk_sentences)
        chunks.append({
            "id": len(chunks),
            "text": chunk_text
        })
    
    # If we have more than 20 chunks, consolidate them
    if len(chunks) > 20:
        all_text = " ".join(chunk["text"] for chunk in chunks)
        sentences = sent_tokenize(all_text)
        sentences_per_chunk = len(sentences) // 20 + (1 if len(sentences) % 20 > 0 else 0)
        
        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk_sentences = sentences[i:i+sentences_per_chunk]
            chunk_text = " ".join(chunk_sentences)
            chunks.append({
                "id": len(chunks),
                "text": chunk_text
            })
    
    print(f"Split document into {len(chunks)} chunks")
    return chunks

def build_chunk_preview(text: str, max_tokens: int = DEFAULT_ROUTING_PREVIEW_TOKENS) -> str:
    """
    Return a preview that fits within the routing model context window.
    We sample the beginning, middle, and end of each chunk so the router
    still has global coverage without sending the full text.
    """
    tokenizer = tiktoken.get_encoding(TOKENIZER_NAME)
    tokens = tokenizer.encode(text)

    if len(tokens) <= max_tokens:
        return text

    segment_tokens = max(max_tokens // 3, 1)
    head_tokens = tokens[:segment_tokens]
    mid_start = max(len(tokens) // 2 - segment_tokens // 2, 0)
    mid_tokens = tokens[mid_start:mid_start + segment_tokens]
    tail_tokens = tokens[-segment_tokens:]

    head = tokenizer.decode(head_tokens).strip()
    middle = tokenizer.decode(mid_tokens).strip()
    tail = tokenizer.decode(tail_tokens).strip()

    return f"{head}\n...\n{middle}\n...\n{tail}"

def route_chunks(question: str, chunks: List[Dict[str, Any]], 
                depth: int, scratchpad: str = "") -> Dict[str, Any]:
    """Ask the model which chunks contain information relevant to the question."""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    print(f"\n==== ROUTING AT DEPTH {depth} ====")
    print(f"Evaluating {len(chunks)} chunks for relevance")
    
    system_message = """You are an expert document navigator. Your task is to:
        1. Identify which text chunks might contain information to answer the user's question
        2. Record your reasoning in a scratchpad for later reference
        3. Choose chunks that are most likely relevant. Be selective, but thorough.

        First think carefully about what information would help answer the question, then evaluate each chunk.
        """
    
    user_message = f"QUESTION: {question}\n\n"
    
    if scratchpad:
        user_message += f"CURRENT SCRATCHPAD:\n{scratchpad}\n\n"
    
    user_message += "TEXT CHUNKS:\n\n"
    
    for chunk in chunks:
        preview = build_chunk_preview(chunk["text"])
        user_message += f"CHUNK {chunk['id']} (preview):\n{preview}\n\n"
    
    tools = [
        {
            "type": "function",
            "name": "update_scratchpad",
            "description": "Record your reasoning about why certain chunks were selected",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Your reasoning about the chunk(s) selection"
                    }
                },
                "required": ["text"],
                "additionalProperties": False
            }
        }
    ]
    
    text_format = {
        "format": {
            "type": "json_schema",
            "name": "selected_chunks",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "chunk_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "IDs of the selected chunks"
                    }
                },
                "required": ["chunk_ids"],
                "additionalProperties": False
            }
        }
    }
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message + "\n\nFirst, you must use the update_scratchpad function to record your reasoning."}
    ]
    
    response = client.responses.create(
        model="gpt-4.1",
        input=messages,
        tools=tools,
        tool_choice="required"
    )
    
    new_scratchpad = scratchpad
    
    for tool_call in response.output:
        if tool_call.type == "function_call" and tool_call.name == "update_scratchpad":
            args = json.loads(tool_call.arguments)
            scratchpad_entry = f"DEPTH {depth} REASONING:\n{args.get('text', '')}"
            if new_scratchpad:
                new_scratchpad += "\n\n" + scratchpad_entry
            else:
                new_scratchpad = scratchpad_entry
            
            messages.append(tool_call)
            messages.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": "Scratchpad updated successfully."
            })
    
    messages.append({"role": "user", "content": "Now, select the chunks that could contain information to answer the question."})
    
    response_chunks = client.responses.create(
        model="gpt-4.1-mini",
        input=messages,
        text=text_format
    )
    
    selected_ids = []
    if response_chunks.output_text:
        try:
            chunk_data = json.loads(response_chunks.output_text)
            selected_ids = chunk_data.get("chunk_ids", [])
        except json.JSONDecodeError:
            print("Warning: Could not parse structured output as JSON")
    
    print(f"Selected chunks: {', '.join(str(id) for id in selected_ids)}")
    
    return {
        "selected_ids": selected_ids,
        "scratchpad": new_scratchpad
    }

def navigate_to_paragraphs(document_text: str, question: str, max_depth: int = 1) -> Dict[str, Any]:
    """Navigate through the document hierarchy to find relevant paragraphs."""
    scratchpad = ""
    chunks = split_into_20_chunks(document_text, min_tokens=500)
    
    chunk_paths = {}
    for chunk in chunks:
        chunk_paths[chunk["id"]] = str(chunk["id"])
    
    for current_depth in range(max_depth + 1):
        result = route_chunks(question, chunks, current_depth, scratchpad)
        scratchpad = result["scratchpad"]
        selected_ids = result["selected_ids"]
        selected_chunks = [c for c in chunks if c["id"] in selected_ids]
        
        if not selected_chunks:
            print("\nNo relevant chunks found.")
            return {"paragraphs": [], "scratchpad": scratchpad}
        
        if current_depth == max_depth:
            print(f"\nReturning {len(selected_chunks)} relevant chunks at depth {current_depth}")
            for chunk in selected_chunks:
                chunk["display_id"] = chunk_paths[chunk["id"]]
            return {"paragraphs": selected_chunks, "scratchpad": scratchpad}
        
        next_level_chunks = []
        next_chunk_id = 0
        
        for chunk in selected_chunks:
            sub_chunks = split_into_20_chunks(chunk["text"], min_tokens=200)
            for sub_chunk in sub_chunks:
                path = f"{chunk_paths[chunk['id']]}.{sub_chunk['id']}"
                sub_chunk["id"] = next_chunk_id
                chunk_paths[next_chunk_id] = path
                next_level_chunks.append(sub_chunk)
                next_chunk_id += 1
        
        chunks = next_level_chunks
    
    return {"paragraphs": [], "scratchpad": scratchpad}

def generate_answer(question: str, paragraphs: List[Dict[str, Any]], 
                   scratchpad: str) -> Dict[str, Any]:
    """Generate an answer from the retrieved paragraphs."""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    print("\n==== GENERATING ANSWER ====")
    
    valid_citations = [str(p.get("display_id", str(p["id"]))) for p in paragraphs]
    
    if not paragraphs:
        return {
            "answer": "I couldn't find relevant information to answer this question in the document.",
            "citations": []
        }
    
    context = ""
    for paragraph in paragraphs:
        display_id = paragraph.get("display_id", str(paragraph["id"]))
        context += f"PARAGRAPH {display_id}:\n{paragraph['text']}\n\n"
    
    system_prompt = f"""You are a legal research assistant answering questions about documents.

        Answer questions based ONLY on the provided paragraphs. Do not rely on any foundation knowledge or external information.
        Cite phrases of the paragraphs that are relevant to the answer.
        Include citations to paragraph IDs for every statement in your answer. Valid citation IDs are: {', '.join(valid_citations)}
        Keep your answer clear, precise, and professional.
        """
    
    user_prompt = f"QUESTION: {question}\n\nSCRATCHPAD (Navigation reasoning):\n{scratchpad}\n\nPARAGRAPHS:\n{context}"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    
    answer_text = response.choices[0].message.content
    
    print(f"\nAnswer: {answer_text}")
    print(f"Valid Citations: {valid_citations}")
    
    return {
        "answer": answer_text,
        "citations": valid_citations
    }

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Legal Document RAG API", "status": "running"}

@app.post("/api/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document and store its path in MongoDB."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save file
    file_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{file.filename}"
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process document to get metadata
        doc_data = load_document_from_file(str(file_path))
        
        # Store in MongoDB
        db = get_database()
        document = {
            "filename": file.filename,
            "file_path": str(file_path),
            "upload_date": datetime.utcnow(),
            "page_count": doc_data["page_count"],
            "word_count": doc_data["word_count"],
            "token_count": doc_data["token_count"]
        }
        
        result = await db[COLLECTION_NAME].insert_one(document)
        
        return DocumentResponse(
            id=str(result.inserted_id),
            filename=file.filename,
            upload_date=document["upload_date"].isoformat(),
            file_path=str(file_path),
            page_count=doc_data["page_count"],
            word_count=doc_data["word_count"],
            token_count=doc_data["token_count"]
        )
    except Exception as e:
        # Clean up file if database insert fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents", response_model=List[DocumentResponse])
async def list_documents():
    """List all uploaded documents."""
    db = get_database()
    documents = []
    
    async for doc in db[COLLECTION_NAME].find():
        documents.append(DocumentResponse(
            id=str(doc["_id"]),
            filename=doc["filename"],
            upload_date=doc["upload_date"].isoformat(),
            file_path=doc["file_path"],
            page_count=doc.get("page_count"),
            word_count=doc.get("word_count"),
            token_count=doc.get("token_count")
        ))
    
    return documents

@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about a specific document."""
    db = get_database()
    
    # Get document from MongoDB
    try:
        doc = await db[COLLECTION_NAME].find_one({"_id": ObjectId(request.document_id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = doc["file_path"]
    
    # Check if file exists
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")
    
    # Load document text
    doc_data = load_document_from_file(file_path)
    document_text = doc_data["text"]
    
    # Navigate and find relevant paragraphs
    navigation_result = navigate_to_paragraphs(document_text, request.question, request.max_depth)
    
    # Generate answer
    answer_data = generate_answer(
        request.question, 
        navigation_result["paragraphs"],
        navigation_result["scratchpad"]
    )
    
    return AnswerResponse(
        answer=answer_data["answer"],
        citations=answer_data["citations"],
        scratchpad=navigation_result["scratchpad"]
    )

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from MongoDB and disk."""
    db = get_database()
    
    try:
        doc = await db[COLLECTION_NAME].find_one({"_id": ObjectId(document_id)})
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    file_path = Path(doc["file_path"])
    if file_path.exists():
        file_path.unlink()
    
    # Delete from MongoDB
    await db[COLLECTION_NAME].delete_one({"_id": ObjectId(document_id)})
    
    return {"message": "Document deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


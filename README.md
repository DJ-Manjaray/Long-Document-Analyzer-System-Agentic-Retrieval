# Long-Document-Analyzer-System-Agentic-Retrieval
RAG-without-Embeddings method, replaces "vector searching" with "intelligent text filtering", Making RAG cheaper, simpler to set up, and often more accurate for complex queries.

Built a simple RAG application for uploading PDF documents and asking intelligent questions using RAG (Retrieval-Augmented Generation) with hierarchical document navigation.

<img width="1453" height="814" alt="image" src="https://github.com/user-attachments/assets/8cf4eb54-4d02-4030-a941-ea6b07c6961c" />

## Features

- 📄 **PDF Upload**: Upload legal documents through a beautiful web interface
- 🗄️ **MongoDB Storage**: Store document metadata and file paths in MongoDB
- 🤖 **Agentic Retrieval Q&A**: Ask questions and get accurate answers with citations
- 🔍 **Hierarchical Navigation**: Multi-depth document chunking for precise information retrieval
- 🎨 **Modern UI**: Beautiful, responsive React frontend with Vite (Built using Cursor)
- ⚡ **Fast Backend**: FastAPI with async MongoDB support

## Architecture

### Backend (FastAPI)
- **PDF Processing**: Extract text from uploaded PDFs using `pypdf`
- **Chunking Strategy**: Hierarchical 20-chunk splitting with sentence boundaries
- **RAG Pipeline**: 
  1. Document chunking with token counting
  2. Agentic Retrieval chunk routing using OpenAI
  3. Recursive navigation through document hierarchy
  4. Answer generation with citations
- **Storage**: MongoDB for metadata, filesystem for PDFs

<img width="1499" height="781" alt="image" src="https://github.com/user-attachments/assets/c90d545b-994c-4df2-9ba7-9b97bc9a1acd" />

### Frontend (React + Vite)
- **Upload Interface**: Drag-and-drop PDF upload
- **Document Management**: View, select, and delete uploaded documents
- **Query Interface**: Ask questions with adjustable search depth
- **Results Display**: Answers with citations and AI reasoning scratchpad

## Prerequisites

- Python 3.12+
- Node.js 16+
- MongoDB (running locally or remote)
- OpenAI API Key

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/DJ-Manjaray/Long-Document-Analyzer-System-Agentic-Retrieval.git
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_api_key_here
# MONGODB_URL=mongodb://localhost:27017
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

### 4. MongoDB Setup

Make sure MongoDB is running:

```bash
# macOS (with Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
# Start MongoDB service from Services or run mongod.exe
```

Or use MongoDB Atlas (cloud):
- Create a free cluster at https://www.mongodb.com/cloud/atlas
- Get connection string and update `MONGODB_URL` in backend/.env

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # Activate venv if not already active
python app.py
```

Backend will run on: http://localhost:8000

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:3000

## Usage

### 1. Upload a Document
- Open http://localhost:3000
- Click "Upload Document" tab
- Select a PDF file
- Wait for upload and processing to complete

### 2. Ask Questions
- Click "Ask Questions" tab
- Select an uploaded document from the dropdown
- Enter your question in the text area
- Adjust search depth (1-3):
  - **1 (Fast)**: Quick search, less thorough
  - **2 (Balanced)**: Good balance of speed and accuracy (default)
  - **3 (Thorough)**: Deep search, most accurate but slower
- Click "Ask Question"
- View answer with citations and AI reasoning

### 3. Manage Documents
- View all uploaded documents with metadata (pages, words, tokens)
- Delete documents by clicking the trash icon

## API Endpoints

### Backend API

- `GET /` - API health check
- `POST /api/upload` - Upload a PDF document
- `GET /api/documents` - List all uploaded documents
- `POST /api/ask` - Ask a question about a document
- `DELETE /api/documents/{document_id}` - Delete a document

## Project Structure

```
Project/
├── backend/
│   ├── app.py              # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment variables (create from .env.example)
│   ├── .env.example       # Example environment variables
│   ├── .gitignore         # Backend gitignore
│   └── uploads/           # Directory for uploaded PDFs (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main React component
│   │   ├── App.css        # Styles for App component
│   │   ├── main.jsx       # React entry point
│   │   └── index.css      # Global styles
│   ├── index.html         # HTML template
│   ├── vite.config.js     # Vite configuration
│   ├── package.json       # Node dependencies
│   └── .gitignore         # Frontend gitignore
│
├── main.py                # Original script (reference)
└── README.md              # This file
```

## Technologies Used

### Backend
- **FastAPI**: Modern, fast web framework for APIs
- **Motor**: Async MongoDB driver
- **PyPDF**: PDF text extraction
- **NLTK**: Natural language processing (sentence tokenization)
- **TikToken**: OpenAI's tokenizer
- **OpenAI**: GPT models for document navigation and Q&A

### Frontend
- **React**: UI library
- **Vite**: Fast build tool
- **Axios**: HTTP client
- **Lucide React**: Beautiful icon library

## Configuration

### Environment Variables (backend/.env)

```env
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URL=mongodb://localhost:27017
```

### MongoDB Collections

The app creates a database named `legal_rag_db` with a collection `documents`:

```javascript
{
  "_id": ObjectId,
  "filename": "document.pdf",
  "file_path": "/path/to/uploads/timestamp_document.pdf",
  "upload_date": ISODate,
  "page_count": 920,
  "word_count": 150000,
  "token_count": 200000
}
```

## 🔥 Unique Features
- ✅ Sentence-aware chunking (never splits mid-sentence)
- ✅ 20-chunk strategy at each level
- ✅ Token counting with TikToken
- ✅ Hierarchical navigation
- ✅ Agentic Retrieval routing with scratchpad
- ✅ Citation tracking


## How It Works


### Document Processing Pipeline

1. **Upload**: User uploads PDF via frontend
2. **Storage**: Backend saves file to `uploads/` directory
3. **Extraction**: PyPDF extracts text from all pages
4. **Metadata**: Count pages, words, and tokens
5. **MongoDB**: Store filename, path, and metadata in database

### Question Answering Pipeline

1. **Document Loading**: Load full text from stored PDF
2. **Initial Chunking**: Split document into 20 chunks (~500 tokens each)
3. **Depth 0 Routing**: AI selects relevant chunks
4. **Recursive Navigation**: Selected chunks are split further and re-evaluated
5. **Answer Generation**: AI generates answer from final selected paragraphs
6. **Citation**: Return answer with paragraph citations and reasoning scratchpad

### Hierarchical Navigation

The system uses a tree-like navigation:
- **Depth 0**: 20 high-level chunks
- **Depth 1**: Selected chunks split into 20 sub-chunks each
- **Depth 2**: Further refinement for precision

Each level uses OpenAI to intelligently select relevant chunks, maintaining a "scratchpad" of reasoning.

# System Architecture

![Screen Recording 2025-12-27 at 12 04 18](https://github.com/user-attachments/assets/6acb1954-58b2-43d2-a71c-0daa17bb7491)


## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                    http://localhost:3000                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    REACT FRONTEND (Vite)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Upload Tab     │  │  Query Tab      │  │  Document List  │ │
│  │  - File picker  │  │  - Doc selector │  │  - View docs    │ │
│  │  - Upload PDF   │  │  - Ask question │  │  - Delete docs  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Axios HTTP
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  FASTAPI BACKEND (Python)                        │
│                   http://localhost:8000                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                            │  │
│  │  • POST /api/upload      → Upload & process PDF          │  │
│  │  • GET  /api/documents   → List all documents            │  │
│  │  • POST /api/ask         → Question answering            │  │
│  │  • DELETE /api/documents/{id} → Delete document          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Document Processing Pipeline                             │  │
│  │  1. PDF Upload Handler                                    │  │
│  │  2. Text Extraction (PyPDF)                               │  │
│  │  3. Token Counting (TikToken)                             │  │
│  │  4. Metadata Calculation                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  RAG Pipeline (Question Answering)                        │  │
│  │  1. Document Loading                                      │  │
│  │  2. Hierarchical Chunking                                 │  │
│  │  3. Agentic Retrieval Routing                                    │  │
│  │  4. Answer Generation                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────┬────────────────────────┬───────────────────────┘
                │                        │
                │                        │
                ▼                        ▼
    ┌───────────────────┐    ┌──────────────────────┐
    │   FILE SYSTEM     │    │   MONGODB DATABASE   │
    │                   │    │                      │
    │  uploads/         │    │  legal_rag_db        │
    │  └─ PDFs stored   │    │  └─ documents        │
    │     with timestamp│    │     collection       │
    └───────────────────┘    └──────────────────────┘
                │                        │
                └────────────┬───────────┘
                             │
                    ┌────────▼─────────┐
                    │   OPENAI API     │
                    │   GPT-4.1        │
                    │   - Chunk routing│
                    │   - Answer gen   │
                    └──────────────────┘
```

## Data Flow

### 1. PDF Upload Flow

```
User selects PDF
    ↓
Frontend sends multipart/form-data
    ↓
Backend receives file
    ↓
Save to uploads/ directory
    ↓
Extract text with PyPDF
    ↓
Calculate metadata (pages, words, tokens)
    ↓
Store metadata in MongoDB
    ↓
Return document info to frontend
```

### 2. Question Answering Flow

```
User asks question about document
    ↓
Frontend sends {document_id, question, max_depth}
    ↓
Backend retrieves file path from MongoDB
    ↓
Load PDF text from file system
    ↓
┌─────────────────────────────────────┐
│   RAG PIPELINE                      │
├─────────────────────────────────────┤
│ DEPTH 0:                            │
│  - Split text into 20 chunks        │
│  - Send to OpenAI for routing       │
│  - OpenAI selects relevant chunks   │
│  - Update scratchpad                │
├─────────────────────────────────────┤
│ DEPTH 1 (if max_depth ≥ 1):        │
│  - Split selected chunks into 20    │
│  - Route again with OpenAI          │
│  - Refine selection                 │
├─────────────────────────────────────┤
│ DEPTH 2 (if max_depth ≥ 2):        │
│  - Further split and route          │
│  - Maximum precision                │
├─────────────────────────────────────┤
│ FINAL:                              │
│  - Send selected paragraphs to AI   │
│  - Generate answer with citations   │
└─────────────────────────────────────┘
    ↓
Return {answer, citations, scratchpad}
    ↓
Frontend displays results
```

## MongoDB Document Schema

```javascript
// Collection: documents
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "filename": "legal_document.pdf",
  "file_path": "/uploads/1703001234.567_legal_document.pdf",
  "upload_date": ISODate("2024-12-26T10:30:00Z"),
  "page_count": 920,
  "word_count": 245678,
  "token_count": 342156
}
```

## File System Structure

```
uploads/
├── 1703001234.567_document1.pdf
├── 1703002345.678_document2.pdf
└── 1703003456.789_document3.pdf

Note: Files are prefixed with timestamp to avoid name collisions
```

## RAG Pipeline Details

### Chunking Strategy

```
Original Document (200,000 tokens)
        ↓
┌───────────────────────────┐
│ LEVEL 0: 20 chunks        │
│ (~10,000 tokens each)     │
└───────────────────────────┘
        ↓ (AI selects 3)
┌───────────────────────────┐
│ LEVEL 1: 60 sub-chunks    │
│ (~500 tokens each)        │
└───────────────────────────┘
        ↓ (AI selects 5)
┌───────────────────────────┐
│ LEVEL 2: 100 paragraphs   │
│ (~200 tokens each)        │
└───────────────────────────┘
        ↓ (AI selects 3)
┌───────────────────────────┐
│ FINAL: 3 paragraphs       │
│ Used for answer generation│
└───────────────────────────┘
```

### Sentence-Aware Chunking

The system never splits in the middle of a sentence:

```python
# Example chunking process
sentences = ["Sentence 1.", "Sentence 2.", "Sentence 3.", ...]
    ↓
Group sentences into chunks
    ↓
Ensure minimum token count (500)
    ↓
Never exceed 2x minimum (1000)
    ↓
Result: Clean chunks with complete sentences
```

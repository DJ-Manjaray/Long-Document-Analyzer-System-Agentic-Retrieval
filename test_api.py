"""
Test script for the Long Document Analyzer System - Agentic Retrieval
Run this after starting the backend server to verify everything works
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PDF_PATH = "test_document.pdf"  # You need a test PDF file

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_health_check():
    """Test 1: Health check endpoint"""
    print_section("Test 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print("❌ Health check failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_list_documents():
    """Test 2: List all documents"""
    print_section("Test 2: List Documents")
    
    try:
        response = requests.get(f"{BASE_URL}/api/documents")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            documents = response.json()
            print(f"Found {len(documents)} documents")
            for doc in documents:
                print(f"\n  - {doc['filename']}")
                print(f"    ID: {doc['id']}")
                print(f"    Pages: {doc.get('page_count', 'N/A')}")
                print(f"    Words: {doc.get('word_count', 'N/A')}")
            print("✅ List documents passed!")
            return True, documents
        else:
            print("❌ List documents failed!")
            return False, []
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, []

def test_upload_document(pdf_path):
    """Test 3: Upload a PDF document"""
    print_section("Test 3: Upload Document")
    
    if not Path(pdf_path).exists():
        print(f"⚠️  Test PDF not found: {pdf_path}")
        print("Please create a test PDF or update TEST_PDF_PATH in the script")
        return False, None
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            doc = response.json()
            print(f"✅ Upload successful!")
            print(f"\nDocument Info:")
            print(f"  ID: {doc['id']}")
            print(f"  Filename: {doc['filename']}")
            print(f"  Pages: {doc.get('page_count', 'N/A')}")
            print(f"  Words: {doc.get('word_count', 'N/A')}")
            print(f"  Tokens: {doc.get('token_count', 'N/A')}")
            return True, doc
        else:
            print(f"❌ Upload failed!")
            print(f"Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_ask_question(document_id, question="What is this document about?", max_depth=2):
    """Test 4: Ask a question about a document"""
    print_section("Test 4: Ask Question")
    
    print(f"Document ID: {document_id}")
    print(f"Question: {question}")
    print(f"Max Depth: {max_depth}")
    print("\nProcessing... (this may take 30-60 seconds)\n")
    
    try:
        payload = {
            "document_id": document_id,
            "question": question,
            "max_depth": max_depth
        }
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/ask", json=payload)
        elapsed_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Question answered successfully!")
            print(f"\n📝 ANSWER:")
            print("-" * 60)
            print(result['answer'])
            print("-" * 60)
            
            if result.get('citations'):
                print(f"\n📚 CITATIONS:")
                for citation in result['citations']:
                    print(f"  - Paragraph {citation}")
            
            if result.get('scratchpad'):
                print(f"\n🧠 AI REASONING (Scratchpad):")
                print("-" * 60)
                print(result['scratchpad'])
                print("-" * 60)
            
            return True
        else:
            print(f"❌ Question failed!")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_delete_document(document_id):
    """Test 5: Delete a document"""
    print_section("Test 5: Delete Document")
    
    print(f"Deleting document ID: {document_id}")
    
    try:
        response = requests.delete(f"{BASE_URL}/api/documents/{document_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Document deleted successfully!")
            return True
        else:
            print(f"❌ Delete failed!")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("  Long Document Analyzer System - Agentic Retrieval - API TESTS")
    print("🚀" * 30)
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n❌ Backend is not running! Please start the backend server first.")
        print("   Run: cd backend && python app.py")
        return
    
    # Test 2: List existing documents
    success, existing_docs = test_list_documents()
    
    # Test 3: Upload document (optional, only if test PDF exists)
    uploaded_doc = None
    if Path(TEST_PDF_PATH).exists():
        success, uploaded_doc = test_upload_document(TEST_PDF_PATH)
    else:
        print_section("Test 3: Upload Document")
        print("⚠️  Skipping upload test (no test PDF found)")
    
    # Test 4: Ask question (use uploaded or existing document)
    test_doc = uploaded_doc if uploaded_doc else (existing_docs[0] if existing_docs else None)
    
    if test_doc:
        # Try a few different questions
        questions = [
            "What is this document about?",
            "What are the main topics covered?",
            "Summarize the key points."
        ]
        
        # Ask just one question for testing
        test_ask_question(test_doc['id'], questions[0], max_depth=1)
    else:
        print_section("Test 4: Ask Question")
        print("⚠️  Skipping question test (no documents available)")
    
    # Test 5: Delete document (only if we uploaded one for testing)
    if uploaded_doc:
        delete_choice = input("\n🗑️  Delete the test document? (y/n): ").strip().lower()
        if delete_choice == 'y':
            test_delete_document(uploaded_doc['id'])
    
    # Final summary
    print_section("Test Summary")
    print("✅ All tests completed!")
    print("\n📝 Next steps:")
    print("  1. Open http://localhost:3000 to use the web interface")
    print("  2. Upload a PDF document")
    print("  3. Ask questions about your document")
    print("\n" + "🎉" * 30 + "\n")

if __name__ == "__main__":
    main()


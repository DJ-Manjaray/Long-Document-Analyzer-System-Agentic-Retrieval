import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, MessageSquare, Loader, Trash2, Send, CheckCircle } from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [maxDepth, setMaxDepth] = useState(2);
  const [activeTab, setActiveTab] = useState('upload');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/documents`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      await fetchDocuments();
      event.target.value = '';
      setActiveTab('query');
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!selectedDocument || !question.trim()) {
      alert('Please select a document and enter a question');
      return;
    }

    setLoading(true);
    setAnswer(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/ask`, {
        document_id: selectedDocument.id,
        question: question,
        max_depth: maxDepth,
      });
      setAnswer(response.data);
    } catch (error) {
      console.error('Error asking question:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/api/documents/${docId}`);
      await fetchDocuments();
      if (selectedDocument?.id === docId) {
        setSelectedDocument(null);
        setAnswer(null);
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Error deleting document: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <FileText className="header-icon" size={32} />
            <div>
              <h1>Long Document Analyzer System - Agentic Retrieval</h1>
              <p className="subtitle">RAG-without-Embeddings mehod</p>
            </div>
          </div>
        </header>

        <div className="tabs">
          <button
            className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <Upload size={18} />
            Upload Document
          </button>
          <button
            className={`tab ${activeTab === 'query' ? 'active' : ''}`}
            onClick={() => setActiveTab('query')}
          >
            <MessageSquare size={18} />
            Ask Questions
          </button>
        </div>

        <div className="content">
          {activeTab === 'upload' && (
            <div className="upload-section">
              <div className="upload-card">
                <Upload className="upload-icon" size={48} />
                <h2>Upload PDF Document</h2>
                <p className="upload-description">
                  Upload legal documents to analyze with Agentic Retrieval question answering
                </p>
                <label className="upload-button">
                  {uploading ? (
                    <>
                      <Loader className="spinner" size={20} />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload size={20} />
                      Choose PDF File
                    </>
                  )}
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    style={{ display: 'none' }}
                  />
                </label>
              </div>

              <div className="documents-list">
                <h3>Uploaded Documents ({documents.length})</h3>
                {documents.length === 0 ? (
                  <p className="empty-state">No documents uploaded yet</p>
                ) : (
                  <div className="documents-grid">
                    {documents.map((doc) => (
                      <div key={doc.id} className="document-card">
                        <div className="document-info">
                          <FileText className="doc-icon" size={24} />
                          <div className="doc-details">
                            <h4>{doc.filename}</h4>
                            <div className="doc-metadata">
                              {doc.page_count && <span>{doc.page_count} pages</span>}
                              {doc.word_count && <span>{doc.word_count.toLocaleString()} words</span>}
                              {doc.token_count && <span>{doc.token_count.toLocaleString()} tokens</span>}
                            </div>
                            <p className="doc-date">
                              {new Date(doc.upload_date).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <button
                          className="delete-button"
                          onClick={() => handleDeleteDocument(doc.id)}
                          title="Delete document"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'query' && (
            <div className="query-section">
              <div className="query-card">
                <h2>Ask a Question</h2>
                
                <div className="form-group">
                  <label>Select Document</label>
                  <select
                    value={selectedDocument?.id || ''}
                    onChange={(e) => {
                      const doc = documents.find(d => d.id === e.target.value);
                      setSelectedDocument(doc);
                      setAnswer(null);
                    }}
                    className="select-input"
                  >
                    <option value="">Choose a document...</option>
                    {documents.map((doc) => (
                      <option key={doc.id} value={doc.id}>
                        {doc.filename}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedDocument && (
                  <div className="selected-doc-info">
                    <CheckCircle size={16} />
                    <span>{selectedDocument.filename} selected</span>
                  </div>
                )}

                <div className="form-group">
                  <label>Your Question</label>
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g., What format should a motion to compel discovery be filed in?"
                    className="question-input"
                    rows={4}
                  />
                </div>

                <div className="form-group">
                  <label>
                    Search Depth: {maxDepth}
                    <span className="depth-info">(Higher = more thorough but slower)</span>
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="3"
                    value={maxDepth}
                    onChange={(e) => setMaxDepth(parseInt(e.target.value))}
                    className="depth-slider"
                  />
                  <div className="depth-labels">
                    <span>Fast</span>
                    <span>Balanced</span>
                    <span>Thorough</span>
                  </div>
                </div>

                <button
                  className="ask-button"
                  onClick={handleAskQuestion}
                  disabled={loading || !selectedDocument || !question.trim()}
                >
                  {loading ? (
                    <>
                      <Loader className="spinner" size={20} />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Send size={20} />
                      Ask Question
                    </>
                  )}
                </button>
              </div>

              {answer && (
                <div className="answer-section">
                  <h3>Answer</h3>
                  <div className="answer-content">
                    <p>{answer.answer}</p>
                  </div>

                  {answer.citations && answer.citations.length > 0 && (
                    <div className="citations">
                      <h4>Citations</h4>
                      <div className="citation-tags">
                        {answer.citations.map((citation, index) => (
                          <span key={index} className="citation-tag">
                            Paragraph {citation}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {answer.scratchpad && (
                    <details className="scratchpad">
                      <summary>View AI Reasoning Process</summary>
                      <pre>{answer.scratchpad}</pre>
                    </details>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;


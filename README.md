# 🕵️ SIMPLE-RAG-SYSTEM

A lightweight Retrieval-Augmented Generation (RAG) application built with Python and Streamlit that allows users to upload evidence files, create a searchable knowledge index, and query the data using intelligent document retrieval techniques.

## 🚀 Overview

SIMPLE-RAG-SYSTEM acts as an AI-powered investigation assistant.

Users can:

- Upload evidence files (TXT, logs, documents)
- Automatically ingest and index uploaded content
- Search evidence using natural language questions
- Retrieve the most relevant information using TF-IDF similarity search
- Analyze uploaded files through a clean Streamlit interface

## ✨ Features

- 📂 Multi-file upload support
- 🔍 Automatic document indexing
- 🧠 Retrieval-Augmented Question Answering
- 📊 TF-IDF based semantic retrieval
- 🎯 Evidence-focused search
- 💻 Streamlit web interface
- ⚡ Lightweight and easy to run locally

---

## 🏗️ Project Structure

```bash
SIMPLE-RAG-SYSTEM/
│
├── backend/
│   ├── ingest.py          # File ingestion and indexing
│   └── investigator.py    # Query answering engine
│
├── frontend/
│   ├── ui.py              # Streamlit UI
│   └── data/
│       ├── uploads/
│       └── index.json
│
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

## ⚙️ How It Works

### 1. Upload Evidence

Users upload text files or logs through the Streamlit interface.

### 2. Ingestion

The system:

- Saves uploaded files
- Reads document contents
- Splits text into sentences
- Tokenizes content
- Builds a searchable index

### 3. Retrieval

When a question is asked:

- Query is converted into TF-IDF vectors
- Similarity scores are calculated
- Most relevant sentences are retrieved

### 4. Response Generation

The system returns:

- Relevant evidence
- Supporting files
- Context-aware answers

---

## 🛠️ Technologies Used

- Python
- Streamlit
- Scikit-Learn
- TF-IDF Vectorization
- JSON Index Storage

## ▶️ Run Application

Start the Streamlit app:

```bash
streamlit run frontend/ui.py
```

The application will open in your browser at:

```text
http://localhost:8501
```

---

## 📝 Example Workflow

### Upload Files

```text
network_alerts.txt
student_chat.txt
```

### Ask Questions

```text
Who is the prime suspect?
```

```text
What happened at 2 AM?
```

```text
Summarize suspicious activity.
```

The system retrieves the most relevant evidence from the indexed files.

---

## 🔍 Retrieval Method

The current version uses:

### TF-IDF Similarity Search

- Sentence tokenization
- Query vectorization
- Cosine similarity ranking
- Top relevant evidence extraction

Fallback retrieval is provided using keyword overlap when TF-IDF is unavailable.

---

## 📌 Future Improvements

- OpenAI/Gemini integration
- Vector databases (FAISS/Chroma)
- PDF support
- Embedding-based semantic search
- Multi-document summarization
- Chat history memory
- Advanced RAG pipelines


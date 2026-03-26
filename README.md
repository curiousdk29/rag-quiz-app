# Smart Study Assistant — RAG-Powered Quiz App

An AI-powered study tool that lets you upload your notes (PDF) and:
- Chat with your notes using Retrieval-Augmented Generation (RAG)
- Generate MCQ quizzes from your notes automatically
- Track your performance and identify weak areas
- Get targeted questions on topics you consistently get wrong

## Tech Stack
- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: Google text-embedding-004
- **Vector DB**: ChromaDB (per-document collections)
- **Orchestration**: LangChain (LCEL)
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Progress DB**: SQLite

## Architecture
```
PDF Upload → PyPDF → Chunking → Embeddings → ChromaDB
User Query → Embed Query → ChromaDB Search → Top 3 Chunks → Gemini → Answer
```

## Setup

1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/rag-quiz-app.git
cd rag-quiz-app
```

2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Add your API key — create a `.env` file:
```
GOOGLE_API_KEY=your_key_here
```
Get a free key at https://aistudio.google.com/app/apikey

5. Run the backend
```bash
uvicorn main:app --reload
```

6. Run the frontend (new terminal)
```bash
streamlit run app.py
```

7. Open http://localhost:8501

## Project Structure
```
rag-quiz-app/
├── ingest.py       # PDF loading, chunking, embedding, ChromaDB storage
├── query.py        # RAG chain, quiz generation, weak area quiz
├── main.py         # FastAPI backend (upload, query, quiz, stats endpoints)
├── app.py          # Streamlit frontend
├── database.py     # SQLite operations for quiz attempt tracking
└── requirements.txt
```
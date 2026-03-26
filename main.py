from fastapi import FastAPI, UploadFile, File
import os
from ingest import ingest_pdf  # Import your previous function
from query import ask_question, generate_quiz  # Import your query logic and quiz generation logic
from database import init_db, save_attempt, get_weak_areas, get_all_stats
from query import generate_weak_area_quiz
from pydantic import BaseModel
from query import ask_question  # Import your query logic

app = FastAPI()

init_db()

uploaded_collections: dict[str, str] = {} 

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    try:
        result = ingest_pdf(file_path)
        uploaded_collections[file.filename] = result["collection"]
        return {
            "message": f"Successfully ingested {file.filename}",
            "collection": result["collection"],
            "pages_loaded": result["pages"],
            "chunks_stored": result["chunks"]
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)




@app.get("/collections")
def list_collections():
    return {"collections": uploaded_collections}

class QueryRequest(BaseModel):
    question: str
    collection: str = "default"

@app.post("/query")
async def query_pdf(request: QueryRequest):
    result = ask_question(request.question, collection_name=request.collection)
    return result

@app.post("/generate-quiz")
async def get_quiz(collection: str = "default"):
    quiz = generate_quiz(collection_name=collection)
    return {"quiz": quiz}
    
# save-attempt now takes collection
class AttemptRequest(BaseModel):
    question: str
    topic: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    collection: str = "default"

@app.post("/save-attempt")
def save_quiz_attempt(request: AttemptRequest):
    save_attempt(
        collection=request.collection,
        question=request.question,
        topic=request.topic,
        user_answer=request.user_answer,
        correct_answer=request.correct_answer,
        is_correct=request.is_correct
    )
    return {"message": "Attempt saved", "topic": request.topic}


# weak-areas now filtered by collection
@app.get("/weak-areas")
def weak_areas(collection: str = "default"):
    return {"weak_areas": get_weak_areas(collection)}


# stats now filtered by collection
@app.get("/stats")
def stats(collection: str = "default"):
    return {"stats": get_all_stats(collection)}


# weak-area-quiz passes collection through to query
@app.post("/weak-area-quiz")
def weak_area_quiz(collection: str = "default"):
    quiz = generate_weak_area_quiz(collection_name=collection)
    if not quiz:
        return {
            "message": "No weak areas detected yet. Complete some quizzes first!",
            "quiz": []
        }
    return {"quiz": quiz}
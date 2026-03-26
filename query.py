# query.py

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from ingest import get_vectorstore    # reusing from ingest.py
from langchain_core.output_parsers import JsonOutputParser
from database import get_weak_areas

LLM_MODEL = "gemini-2.5-flash"

def get_llm():
    return ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.3)

def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

def ask_question(question: str, collection_name: str = "default") -> dict:

    vectorstore = get_vectorstore(collection_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template("""
You are a helpful study assistant. Answer the question using ONLY the context below.
If the answer isn't in the context, say "I couldn't find that in your notes."

Context:
{context}

Question: {question}
""")

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(question)

    # Collect sources separately
    source_docs = retriever.invoke(question)
    sources = [
        {
            "page": doc.metadata.get("page", "?"),
            "preview": doc.page_content[:150]
        }
        for doc in source_docs
    ]

    return {"answer": answer, "sources": sources}

# Add this to your query.py

def generate_quiz(collection_name: str = "default") -> list:
    vectorstore = get_vectorstore(collection_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = get_llm()

    quiz_prompt = ChatPromptTemplate.from_template("""
You are an expert professor. Based on the provided context, generate 3 MCQs.
Return the response ONLY as a JSON list of objects.

Each object must have these exact keys:
- "question": the quiz question
- "options": a list of 4 strings
- "answer": the correct string from the options
- "explanation": a 1-sentence explanation why it is correct
- "topic": a short 2-4 word label for the concept being tested (e.g. "Zero-Day Detection")

Context:
{context}
""")

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | quiz_prompt
        | llm
        | JsonOutputParser()
    )

    return chain.invoke("Generate a comprehensive quiz.")


def generate_weak_area_quiz(collection_name: str = "default") -> list:
    weak_areas = get_weak_areas(collection_name)   # pass collection here too
    if not weak_areas:
        return []

    topics_str = ", ".join([w["topic"] for w in weak_areas])
    vectorstore = get_vectorstore(collection_name)  # and here
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = get_llm()

    prompt = ChatPromptTemplate.from_template("""
You are an expert professor. The student is struggling with: {topics}

Based on the context below, generate 3 MCQs targeting these weak areas.
Return ONLY a JSON list. Each object must have:
- "question": the quiz question
- "options": a list of 4 strings
- "answer": the correct string from options
- "explanation": 1-sentence explanation
- "topic": short 2-4 word label matching one of the weak area topics

Context:
{context}
""")

    chain = (
        {"context": retriever | format_docs, "topics": RunnablePassthrough()}
        | prompt
        | llm
        | JsonOutputParser()
    )

    return chain.invoke(topics_str)
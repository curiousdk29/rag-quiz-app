# app.py

import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Study Companion", layout="wide")
st.title("Smart Study Assistant")

# --- Sidebar ---
with st.sidebar:
    st.header("Upload Notes")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    if st.button("Process PDF"):
        if uploaded_file:
            response = requests.post(
                f"{API}/upload",
                files={"file": (uploaded_file.name, uploaded_file.getvalue())}
            )
            data = response.json()
            st.success(data["message"])
            st.session_state.active_collection = data["collection"]
        else:
            st.warning("Please upload a PDF first.")

    st.divider()

    # Collection selector
    collections_res = requests.get(f"{API}/collections")
    collections = collections_res.json().get("collections", {})

    if collections:
        selected_file = st.selectbox("Active PDF", list(collections.keys()))
        st.session_state.active_collection = collections[selected_file]

    st.divider()

    # Weak areas — scoped to active collection
    active_col = st.session_state.get("active_collection", "default")
    st.header("Weak Areas")
    weak_res = requests.get(f"{API}/weak-areas", params={"collection": active_col})
    weak_areas = weak_res.json().get("weak_areas", [])

    if weak_areas:
        for w in weak_areas:
            st.error(f"{w['topic']} — {w['error_rate']}% error rate")
    else:
        st.info("No weak areas yet for this PDF.")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Chat", "Quiz", "Progress"])

active_col = st.session_state.get("active_collection", "default")

# ===================== TAB 1: CHAT =====================
with tab1:
    st.subheader("Ask about your notes")
    user_input = st.chat_input("Ask a question...")

    if user_input:
        res = requests.post(f"{API}/query", json={
            "question": user_input,
            "collection": active_col
        })
        data = res.json()
        st.write("**Answer:**", data["answer"])
        with st.expander("View Sources"):
            for source in data["sources"]:
                st.info(f"Page {source['page']}: {source['preview']}...")

# ===================== TAB 2: QUIZ =====================
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Quiz from Notes"):
            with st.spinner("Generating questions..."):
                res = requests.post(
                    f"{API}/generate-quiz",
                    params={"collection": active_col}
                )
                st.session_state.quiz = res.json()["quiz"]
                st.session_state.quiz_collection = active_col

    with col2:
        if st.button("Target My Weak Areas"):
            with st.spinner("Generating targeted questions..."):
                res = requests.post(
                    f"{API}/weak-area-quiz",
                    params={"collection": active_col}
                )
                data = res.json()
                if data["quiz"]:
                    st.session_state.quiz = data["quiz"]
                    st.session_state.quiz_collection = active_col
                else:
                    st.warning(data["message"])

    if "quiz" in st.session_state:
        quiz_col = st.session_state.get("quiz_collection", "default")

        for i, item in enumerate(st.session_state.quiz):
            st.write(f"**Q{i+1}: {item['question']}**")
            user_choice = st.radio(
                f"Options for Q{i+1}",
                item["options"],
                key=f"q{i}",
                label_visibility="collapsed"
            )

            if st.button(f"Submit Q{i+1}", key=f"btn{i}"):
                is_correct = user_choice == item["answer"]

                # collection is now included in the save request
                requests.post(f"{API}/save-attempt", json={
                    "question": item["question"],
                    "topic": item["topic"],
                    "user_answer": user_choice,
                    "correct_answer": item["answer"],
                    "is_correct": is_correct,
                    "collection": quiz_col
                })

                if is_correct:
                    st.success("Correct!")
                else:
                    st.error(f"Wrong. Correct answer: {item['answer']}")
                    st.info(f"Explanation: {item['explanation']}")

            st.divider()

# ===================== TAB 3: PROGRESS =====================
with tab3:
    st.subheader(f"Progress for active PDF")

    stats_res = requests.get(f"{API}/stats", params={"collection": active_col})
    stats = stats_res.json().get("stats", [])

    if stats:
        for s in stats:
            st.write(f"**{s['topic']}** — {s['correct']}/{s['total']} correct ({s['accuracy']}%)")
            st.progress(int(s["accuracy"]) / 100)
    else:
        st.info("No attempts yet for this PDF. Take a quiz first!")
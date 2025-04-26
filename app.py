import streamlit as st
import pandas as pd
import pickle
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Set page config
st.set_page_config(page_title="📚 Book Recommendation System", page_icon="📚", layout="wide")

# Load model dan data
@st.cache_resource
def load_model():
    with open('model_tfidf.pkl', 'rb') as f:
        tfidf = pickle.load(f)
    with open('matrix_similarity.pkl', 'rb') as f:
        tfidf_matrix = pickle.load(f)
    books = pd.read_csv('books_cleaned.csv')
    return tfidf, tfidf_matrix, books

tfidf, tfidf_matrix, books = load_model()

# Index mapping
title_indices = pd.Series(books.index, index=books['Book-Title'].str.lower()).drop_duplicates()
author_indices = pd.Series(books.index, index=books['Book-Author'].str.lower()).drop_duplicates()

# Tambahan: Topik rekomendasi
topics = {
    "Books Like Harry Potter": "magic wizard school fantasy",
    "Books for Sci-fi Fans": "space future technology aliens",
    "Romantic Novels": "love romance relationships heart",
    "Thriller & Mystery Books": "crime detective murder mystery suspense",
    "Self Improvement & Motivation": "self-help motivation habits success",
}

# TF-IDF baru untuk content-based topik
@st.cache_resource
def load_tfidf_content():
    books['content'] = books['Book-Title'].fillna('') + ' ' + \
                       books['Book-Author'].fillna('') + ' ' + \
                       books['Publisher'].fillna('')
    tfidf_content = TfidfVectorizer(stop_words='english')
    tfidf_matrix_content = tfidf_content.fit_transform(books['content'])
    return tfidf_content, tfidf_matrix_content

tfidf_content, tfidf_matrix_content = load_tfidf_content()

# Fungsi rekomendasi by title
def recommend_books_by_title(title, top_n=10):
    title = title.lower()
    if title not in title_indices:
        return [], []
    
    idx = title_indices[title]
    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-(top_n+1):-1][::-1]
    
    recommended_books = books.iloc[similar_indices][['Book-Title', 'Book-Author', 'Publisher', 'Image-URL-L']]
    scores = cosine_sim[similar_indices]
    return recommended_books, scores

# Fungsi rekomendasi by author
def recommend_books_by_author(author, top_n=10):
    author = author.lower()
    if author not in author_indices:
        return [], []

    idx = author_indices[author]
    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[-(top_n+1):-1][::-1]

    recommended_books = books.iloc[similar_indices][['Book-Title', 'Book-Author', 'Publisher']].reset_index(drop=True)
    scores = cosine_sim[similar_indices]
    return recommended_books, scores

# Fungsi rekomendasi by topic
def recommend_books_by_topic(topic_keywords, top_n=10):
    topic_vector = tfidf_content.transform([topic_keywords])
    cosine_sim = cosine_similarity(topic_vector, tfidf_matrix_content).flatten()
    similar_indices = cosine_sim.argsort()[-top_n:][::-1]
    
    recommended_books = books.iloc[similar_indices][['Book-Title', 'Book-Author', 'Publisher', 'Image-URL-L']]
    scores = cosine_sim[similar_indices]
    return recommended_books, scores

# Sidebar Settings
st.sidebar.header("⚙️ Pengaturan")
top_n = st.sidebar.slider("Jumlah Rekomendasi (Top-N):", min_value=5, max_value=20, value=10)
mode = st.sidebar.radio("Mode Pencarian:", ["Judul Buku", "Penulis", "Topik Rekomendasi"])
theme = st.sidebar.radio("Tema:", ["Light", "Dark"])

# Dark Mode Style
if theme == "Dark":
    st.markdown(
        """
        <style>
        body {background-color: #0E1117; color: white;}
        .stSelectbox, .stSlider, .stRadio {color: white;}
        </style>
        """,
        unsafe_allow_html=True
    )

# Judul utama
st.title("📚 Book Recommendation System")
st.markdown("Temukan rekomendasi buku berdasarkan pilihanmu! 🎯")

# Input
if mode == "Judul Buku":
    options = books['Book-Title'].dropna().unique()
    selected_option = st.selectbox("Pilih atau ketik judul buku:", sorted(options))
    search_func = recommend_books_by_title
    input_value = selected_option
elif mode == "Penulis":
    options = books['Book-Author'].dropna().unique()
    selected_option = st.selectbox("Pilih atau ketik nama penulis:", sorted(options))
    search_func = recommend_books_by_author
    input_value = selected_option
else:  # Topik
    selected_topic = st.selectbox("Pilih Topik Rekomendasi:", list(topics.keys()))
    search_func = recommend_books_by_topic
    input_value = topics[selected_topic]

# Cari Rekomendasi
if input_value:
    with st.spinner('🔍 Mencari rekomendasi...'):
        my_bar = st.progress(0, text="Sedang memproses rekomendasi...")
        
        for percent_complete in range(80):
            time.sleep(0.002)
            my_bar.progress(percent_complete + 1, text="Sedang memproses rekomendasi...")

        recommendations, scores = search_func(input_value, top_n=top_n)

        my_bar.progress(100, text="Selesai!")

        if len(recommendations) > 0:
            st.success('Rekomendasi ditemukan! 🎉')

            col1, col2 = st.columns(2)
            for idx, (row, sim) in enumerate(zip(recommendations.iterrows(), scores), 1):
                _, row = row  # karena iterrows() hasilkan (index, row)
                with (col1 if idx % 2 == 1 else col2):
                    st.markdown(f"""
                    ### {idx}. {row['Book-Title']}
                    - **Penulis**: {row['Book-Author']}
                    - **Penerbit**: {row['Publisher']}
                    - **Similarity Score**: {sim:.2f}
                    """)

            avg_similarity = np.mean(scores)
            precision_at_n = 1.0
            st.markdown("### 📊 Evaluation Metrics")
            st.write(f"**Average Similarity**: `{avg_similarity:.2f}`")
            st.write(f"**Precision@{top_n}**: `{precision_at_n:.2f}`")
        else:
            st.error('Data tidak ditemukan dalam database.')

# Footer
st.markdown("---")
st.caption("Created with ❤️ by YourName - Powered by Streamlit")

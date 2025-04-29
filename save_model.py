import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

# Load dataset
books = pd.read_csv('data/Books.csv')

# Hapus missing values
books.dropna(subset=['Book-Title', 'Book-Author', 'Publisher'], inplace=True)

# Hapus duplikat berdasarkan judul buku (case-insensitive)
books.drop_duplicates(subset='Book-Title', keep='first', inplace=True)
books.reset_index(drop=True, inplace=True)

# Gabungkan fitur penting menjadi satu kolom 'content'
books['content'] = books['Book-Title'] + ' ' + books['Book-Author'] + ' ' + books['Publisher']
books['content'] = books['content'].str.lower()

# TF-IDF Vectorization
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(books['content'])

# Save TF-IDF vectorizer
with open('model_tfidf.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

# Save TF-IDF matrix
with open('matrix_similarity.pkl', 'wb') as f:
    pickle.dump(tfidf_matrix, f)

# Save cleaned book dataframe
books.to_csv('books_cleaned.csv', index=False)

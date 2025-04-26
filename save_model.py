import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
books = pd.read_csv('data/Books.csv')

# Simple preprocessing
books.dropna(subset=['Book-Title', 'Book-Author', 'Publisher'], inplace=True)
books['content'] = books['Book-Title'] + ' ' + books['Book-Author'] + ' ' + books['Publisher']
books['content'] = books['content'].str.lower()

# TF-IDF Vectorization
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(books['content'])

# Save tfidf vectorizer
with open('model_tfidf.pkl', 'wb') as f:
    pickle.dump(tfidf, f)

# Save tfidf matrix
with open('matrix_similarity.pkl', 'wb') as f:
    pickle.dump(tfidf_matrix, f)

# Save book dataframe
books.to_csv('books_cleaned.csv', index=False)

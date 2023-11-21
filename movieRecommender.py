# Import necessary libraries
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
from fuzzywuzzy import process

# Loading datasets
movies = pd.read_csv('./movies.csv')
ratings = pd.read_csv('./ratings.csv')

# Preprocess movies data
movies['Genre'] = movies['Genre'].apply(lambda x: x.split('|'))

# Binarizing genres
mlb = MultiLabelBinarizer()
genres_binarized = mlb.fit_transform(movies['Genre'])
genres_df = pd.DataFrame(genres_binarized, columns=mlb.classes_)

# Combine genres with movies
movies = movies.join(genres_df)

# Nearest Neighbors Model
model = NearestNeighbors(n_neighbors=6, algorithm='ball_tree')
model.fit(genres_df)

# Function to find closest movie title
def find_closest_title(title):
    all_titles = movies['Title'].tolist()
    closest_title = process.extractOne(title, all_titles)[0]
    return closest_title

# Function to recommend movies
def recommend_movies(input_title):
    movie_title = find_closest_title(input_title)
    movie_idx = movies.index[movies['Title'] == movie_title].tolist()
    
    if not movie_idx:
        return "Movie not found."
    movie_idx = movie_idx[0]
    
    distances, indices = model.kneighbors([genres_df.iloc[movie_idx]])
    recommended_movie_indices = indices[0][1:]  # Exclude the input movie itself
    
    recommended_movies = movies.iloc[recommended_movie_indices]['Title'].tolist()
    return recommended_movies

# Example usage
user_favorite_movie = 'Toy Story'  # User input
recommended_movies = recommend_movies(user_favorite_movie)
print("Movies recommended based on", user_favorite_movie, ":\n", recommended_movies)

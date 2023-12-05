from flask import Flask, jsonify, request, render_template
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
from fuzzywuzzy import process
import pandas as pd
import random

app = Flask(__name__)

# Loading datasets
movies = pd.read_csv('./data/movies.csv')
ratings = pd.read_csv('./data/ratings.csv')

@app.route('/')
def index():
    return render_template('movieRecommender.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    movie_title = request.args.get('title', '')
    recommended_movies = recommend_movies(movie_title)
    return jsonify(recommended_movies)

@app.route('/fan-favorites', methods=['GET'])
def fan_favorites():
    favorites = recommend_fan_favorites()
    return jsonify(favorites)

if __name__ == '__main__':
    app.run(debug=True)

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

# Function to recommend movies based on favorite
def recommend_movies(input_title):
    movie_title = find_closest_title(input_title)
    movie_idx = movies.index[movies['Title'] == movie_title].tolist()
    
    if not movie_idx:
        return "Movie not found."
    movie_idx = movie_idx[0]
    chosen_movie = {
        "title": movies.iloc[movie_idx]['Title'],
        "genre": ", ".join(movies.iloc[movie_idx]['Genre'])
    }

    # Ensure the input for the model has the same feature names as during fitting
    input_features = genres_df.iloc[[movie_idx]]  # Make it a dataframe with the same structure
    distances, indices = model.kneighbors(input_features)
    recommended_movie_indices = indices[0][1:]  # Exclude the input movie itself

    recommended_movies = []
    for idx in recommended_movie_indices:
        movie_info = movies.iloc[idx]
        recommended_movies.append({
            "title": movie_info['Title'],
            "genre": ", ".join(movie_info['Genre'])
        })

    return {"chosenMovie": chosen_movie, "recommendations": recommended_movies}


# Function to recommend random fan favorites (5-star ratings)
def recommend_fan_favorites():
    high_rated = ratings[ratings['Rating'] == 5.0]
    top_movies = high_rated['MovieId'].unique()
    random_top_movies = random.sample(list(top_movies), 5)
    fan_favorites = []
    for movie_id in random_top_movies:
        movie_info = movies[movies['MovieId'] == movie_id].iloc[0]
        fan_favorites.append({
            "title": movie_info['Title'],
            "genre": movie_info['Genre']
        })
    return fan_favorites


# Example usage
user_favorite_movie = 'Toy Story'  # User input
recommended_movies = recommend_movies(user_favorite_movie)
print("Movies recommended based on", user_favorite_movie, ":\n", recommended_movies)

# Recommend random fan favorites
fan_favorites = recommend_fan_favorites()
print("Random fan favorite movies:\n", fan_favorites)

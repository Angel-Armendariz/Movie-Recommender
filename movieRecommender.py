from flask import Flask, jsonify, request, render_template
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
from fuzzywuzzy import process
import pandas as pd
import random

app = Flask(__name__)

# Loading datasets
movies = pd.read_csv('./movies.csv')
ratings = pd.read_csv('./ratings.csv')

#Belal's------------1--start-----------------------------------------------------------------------------
# # Group by MovieId and calculate the mean rating and vote count for each movie
ratings_grouped = ratings.groupby('MovieId').agg(vote_average=('Rating', 'mean'),
                                                  vote_count=('Rating', 'size')).reset_index()

# Merge the movies and the aggregated ratings data on MovieId
movies_with_ratings = movies.merge(ratings_grouped, on='MovieId', how='left')



# Calculate C, the mean rating across all movies
C = movies_with_ratings['vote_average'].mean()

# Calculate m, the minimum number of votes required to be listed, for example, at the 90th percentile
m = movies_with_ratings['vote_count'].quantile(0.90)

# Function to compute the weighted rating for each movie
def weighted_rating(x, m=m, C=C):
    v = x['vote_count']
    R = x['vote_average']
    return (v/(v+m) * R) + (m/(m+v) * C)

# Calculate the score and create a new feature 'score'
movies_with_ratings['score'] = movies_with_ratings.apply(weighted_rating, axis=1)


# Sort movies based on score calculated above
movies_with_ratings = movies_with_ratings.sort_values('score', ascending=False)

# You can now use this DataFrame to make recommendations  ^^

@app.route('/top-rated', methods=['GET'])
def top_rated():
    top_movies = movies_with_ratings.head(10).to_dict(orient='records')
    return jsonify(top_movies)


# Assume this function is defined within the Flask app context where movies_with_ratings is available
def get_weighted_top_movies(n=10):
    return movies_with_ratings.head(n).to_dict(orient='records')

@app.route('/weighted-top', methods=['GET'])
def weighted_top():
    top_movies_weighted = get_weighted_top_movies()
    return jsonify(top_movies_weighted)

# You would call this route to get the top movies based on the weighted rating system

# Merge movies with the aggregated ratings
movies_with_ratings = movies.merge(ratings_grouped, on='MovieId', how='left')

# Assuming the weighted rating calculation is already defined, calculate the scores
movies_with_ratings['score'] = movies_with_ratings.apply(weighted_rating, axis=1)

def recommend_based_on_movie(input_movie_id, n_recommendations=5):
    # Find the input movie's information
    input_movie = movies_with_ratings[movies_with_ratings['MovieId'] == input_movie_id].iloc[0]
    
    # Calculate the similarity score between the input movie and all other movies
    # Here we simply use the Jaccard similarity on genres. You could also use more complex similarity measures.
    movies_with_ratings['similarity'] = movies_with_ratings['Genre'].apply(
        lambda x: len(set(x) & set(input_movie['Genre'])) / len(set(x) | set(input_movie['Genre']))
    )
    
    # Sort based on similarity score and weighted rating score
    recommended_movies = movies_with_ratings.sort_values(
        ['similarity', 'score'], ascending=[False, False]
    ).head(n_recommendations + 1)  # Plus one because the list includes the input movie itself
    
    # Exclude the input movie from the recommendations
    recommended_movies = recommended_movies[recommended_movies['MovieId'] != input_movie_id]
    
    return recommended_movies[['Title', 'Genre', 'score']]


def recommend_based_on_movie(input_movie_id, n_recommendations=5):
    # Find the input movie's information
    input_movie = movies_with_ratings[movies_with_ratings['MovieId'] == input_movie_id].iloc[0]
    
    # Calculate the similarity score between the input movie and all other movies
    # Here we simply use the Jaccard similarity on genres. You could also use more complex similarity measures.
    movies_with_ratings['similarity'] = movies_with_ratings['Genre'].apply(
        lambda x: len(set(x) & set(input_movie['Genre'])) / len(set(x) | set(input_movie['Genre']))
    )
    
    # Sort based on similarity score and weighted rating score
    recommended_movies = movies_with_ratings.sort_values(
        ['similarity', 'score'], ascending=[False, False]
    ).head(n_recommendations + 1)  # Plus one because the list includes the input movie itself
    
    # Exclude the input movie from the recommendations
    recommended_movies = recommended_movies[recommended_movies['MovieId'] != input_movie_id]
    
    return recommended_movies[['Title', 'Genre', 'score']]


@app.route('/recommend/<int:movie_id>')
def movie_recommendations(movie_id):
    recommended = recommend_based_on_movie(movie_id, n_recommendations=5)
    return jsonify(recommended.to_dict(orient='records'))



#Belal's-------1----end----------------------------------------------------------------------------------

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

    distances, indices = model.kneighbors([genres_df.iloc[movie_idx]])
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

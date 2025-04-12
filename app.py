import pickle
import pandas as pd
import requests
import streamlit as st
from PIL import Image

# Load and display the background image
background_image = Image.open("C:\\Users\\sporw\\Desktop\\movie recom\\code\\image.jpg")  # Replace with your image path
st.image(background_image)

def fetch_poster(movie_id):
    try:
        # Make the API request
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=237299669ff73a76b49737a668282c4e&language=en-US'
        )
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
        
        # Parse the JSON response
        data = response.json()
        
        # Debugging: Print the entire API response
        print(f"API Response for Movie ID {movie_id}: {data}")
        
        # Check if 'poster_path' exists and is not None
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            # If 'poster_path' is missing or None, return a placeholder image
            print(f"No poster found for Movie ID {movie_id}")
            return None  # Return None if no poster found
    
    except requests.exceptions.RequestException as e:
        # Handle API request errors (e.g., network issues, invalid API key)
        print(f"Error fetching poster for Movie ID {movie_id}: {e}")
        return None  # Return None in case of error


def fetch_wikipedia_url(movie_title):
    try:
        # Make the API request to Wikipedia
        response = requests.get(
            f'https://en.wikipedia.org/w/api.php?action=opensearch&search={movie_title}&limit=1&namespace=0&format=json'
        )
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
        
        # Parse the JSON response
        data = response.json()
        
        # Return the Wikipedia URL if available
        if data[3]:
            return data[3][0]
        else:
            return None
    except requests.exceptions.RequestException as e:
        # Handle API request errors (e.g., network issues)
        print(f"Error fetching Wikipedia URL for {movie_title}: {e}")
        return None

# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    # Sort movies by similarity scores (excluding the selected movie itself)
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[0:3]
    
    # Create a list of recommended movie titles and posters
    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        print(f"Fetching poster for Movie ID: {movie_id}")  # Debugging line
        # fetch poster from API
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(poster_url)
        else:
            print(f"Poster not found for Movie ID: {movie_id}")  # Debugging line
    
    return recommended_movies, recommended_movies_posters

# Load the movie data and similarity matrix
movies_dict = pickle.load(open('C:\\Users\\sporw\\Desktop\\movie recom\\code\\movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('C:\\Users\\sporw\\Desktop\\movie recom\\code\\similarity.pkl', 'rb'))

# Streamlit app title
st.title('Movie Recommendation System')

# Dropdown to select a movie
option = st.selectbox(
   "Select a movie to get recommendations:",
   movies['title'].values
)

# Button to display recommendations
if st.button('Recommend'):
    names, posters = recommend(option)
    col1, col2, col3 = st.columns(3)
    
    for i, (name, poster) in enumerate(zip(names, posters)):
        with eval(f"col{i+1}"):  # Dynamically select the column
            wikipedia_url = fetch_wikipedia_url(name)
            if wikipedia_url:
                st.markdown(f'<a href="{wikipedia_url}" target="_blank"><img src="{poster}" alt="{name}" style="width:100%"></a>', unsafe_allow_html=True)
            else:
                st.image(poster)
                
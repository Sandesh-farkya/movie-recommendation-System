import pickle
import os
import gdown
import pandas as pd
import requests
import streamlit as st
from PIL import Image


# 🔽 1. Google Drive se similarity.pkl download agar local mein nahi hai
file_id = "1S9NXHZh-3P1kOZI_1LrqPf9MrFwkUR6s"  # Replace with your actual file ID
file_name = "similarity.pkl"

if not os.path.exists(file_name):
    st.warning(f"{file_name} not found. Downloading from Google Drive...")
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, file_name, quiet=False)

# 🔽 2. Load and display background image
if os.path.exists("image.jpg"):
    background_image = Image.open("image.jpg")
    st.image(background_image)

# 🔽 3. TMDB API se poster fetch function
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=237299669ff73a76b49737a668282c4e&language=en-US'
        )
        response.raise_for_status()
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for Movie ID {movie_id}: {e}")
        return None

# 🔽 4. Wikipedia URL fetch
def fetch_wikipedia_url(movie_title):
    try:
        response = requests.get(
            f'https://en.wikipedia.org/w/api.php?action=opensearch&search={movie_title}&limit=1&namespace=0&format=json'
        )
        response.raise_for_status()
        data = response.json()
        if data[3]:
            return data[3][0]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Wikipedia URL for {movie_title}: {e}")
        return None

# 🔽 5. Recommendation logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[0:3]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(poster_url)
    return recommended_movies, recommended_movies_posters

# 🔽 6. Load movie data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# 🔽 7. Streamlit UI
st.title('🎬 Movie Recommendation System')
option = st.selectbox("Select a movie to get recommendations:", movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(option)
    col1, col2, col3 = st.columns(3)
    for i, (name, poster) in enumerate(zip(names, posters)):
        with [col1, col2, col3][i]:
            wikipedia_url = fetch_wikipedia_url(name)
            if wikipedia_url:
                st.markdown(f'<a href="{wikipedia_url}" target="_blank"><img src="{poster}" alt="{name}" style="width:100%"></a>', unsafe_allow_html=True)
            else:
                st.image(poster)

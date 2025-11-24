import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 Movie Recommendation System")
st.markdown("Discover your next favorite movie based on genres, ratings, and more!")

# Cache the data loading function
@st.cache_data
def load_movie_data():
    """Load movie dataset from GitHub"""
    try:
        # Using a popular movie dataset from GitHub
        url = "https://raw.githubusercontent.com/prust/wikipedia-movie-data/master/movies.json"
        response = requests.get(url)
        movies = pd.DataFrame(response.json())
        return movies
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Fallback sample data
        return pd.DataFrame({
            'title': ['The Shawshank Redemption', 'The Godfather', 'The Dark Knight', 
                     'Pulp Fiction', 'Forrest Gump', 'Inception', 'The Matrix',
                     'Goodfellas', 'The Silence of the Lambs', 'Interstellar'],
            'year': [1994, 1972, 2008, 1994, 1994, 2010, 1999, 1990, 1991, 2014],
            'genres': [['Drama'], ['Crime', 'Drama'], ['Action', 'Drama'], 
                      ['Crime', 'Drama'], ['Drama', 'Romance'], ['Action', 'Sci-Fi'],
                      ['Action', 'Sci-Fi'], ['Crime', 'Drama'], ['Crime', 'Thriller'],
                      ['Adventure', 'Drama', 'Sci-Fi']]
        })

# Load data
with st.spinner("Loading movie database..."):
    movies_df = load_movie_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Options")

# Year range filter
if 'year' in movies_df.columns:
    year_min = int(movies_df['year'].min())
    year_max = int(movies_df['year'].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        year_min, year_max, (year_min, year_max)
    )
    filtered_movies = movies_df[
        (movies_df['year'] >= year_range[0]) & 
        (movies_df['year'] <= year_range[1])
    ]
else:
    filtered_movies = movies_df

# Genre filter
if 'genres' in movies_df.columns:
    all_genres = set()
    for genres_list in movies_df['genres'].dropna():
        if isinstance(genres_list, list):
            all_genres.update(genres_list)
    
    if all_genres:
        selected_genres = st.sidebar.multiselect(
            "Select Genres",
            sorted(all_genres),
            default=[]
        )
        
        if selected_genres:
            filtered_movies = filtered_movies[
                filtered_movies['genres'].apply(
                    lambda x: any(genre in x for genre in selected_genres) 
                    if isinstance(x, list) else False
                )
            ]

# Search functionality
st.sidebar.header("🔎 Search Movies")
search_term = st.sidebar.text_input("Search by title")

if search_term:
    filtered_movies = filtered_movies[
        filtered_movies['title'].str.contains(search_term, case=False, na=False)
    ]

# Display count
st.sidebar.markdown(f"**Found {len(filtered_movies)} movies**")

# Main content
tab1, tab2, tab3 = st.tabs(["📋 Browse Movies", "🎲 Random Pick", "📊 Statistics"])

with tab1:
    st.subheader("Movie List")
    
    # Number of movies to display
    num_display = st.slider("Number of movies to display", 5, 50, 10)
    
    # Display movies
    for idx, row in filtered_movies.head(num_display).iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {row['title']}")
                if 'year' in row:
                    st.write(f"**Year:** {row['year']}")
                if 'genres' in row and isinstance(row['genres'], list):
                    st.write(f"**Genres:** {', '.join(row['genres'])}")
                if 'cast' in row and isinstance(row['cast'], list):
                    st.write(f"**Cast:** {', '.join(row['cast'][:3])}")
            
            with col2:
                if st.button("⭐ Recommend Similar", key=f"rec_{idx}"):
                    st.success("Finding similar movies...")
            
            st.divider()

with tab2:
    st.subheader("Get a Random Movie Recommendation")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎲 Pick Random Movie", use_container_width=True):
            if len(filtered_movies) > 0:
                random_movie = filtered_movies.sample(1).iloc[0]
                
                st.success("Here's your recommendation!")
                st.markdown(f"## 🎬 {random_movie['title']}")
                
                if 'year' in random_movie:
                    st.write(f"**Year:** {random_movie['year']}")
                if 'genres' in random_movie and isinstance(random_movie['genres'], list):
                    st.write(f"**Genres:** {', '.join(random_movie['genres'])}")
                if 'cast' in random_movie and isinstance(random_movie['cast'], list):
                    st.write(f"**Cast:** {', '.join(random_movie['cast'][:5])}")
            else:
                st.warning("No movies found with current filters!")

with tab3:
    st.subheader("Movie Database Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Movies", len(movies_df))
    
    with col2:
        if 'year' in movies_df.columns:
            st.metric("Year Range", f"{int(movies_df['year'].min())} - {int(movies_df['year'].max())}")
    
    with col3:
        st.metric("Filtered Results", len(filtered_movies))
    
    # Genre distribution
    if 'genres' in movies_df.columns:
        st.subheader("Top Genres")
        genre_counts = {}
        for genres_list in movies_df['genres'].dropna():
            if isinstance(genres_list, list):
                for genre in genres_list:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        if genre_counts:
            genre_df = pd.DataFrame(
                list(genre_counts.items()), 
                columns=['Genre', 'Count']
            ).sort_values('Count', ascending=False).head(10)
            
            st.bar_chart(genre_df.set_index('Genre'))

# Footer
st.markdown("---")
st.markdown("*Movie data sourced from GitHub repositories*")

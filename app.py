import streamlit as st
import google.generativeai as genai
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from PIL import Image
import io
import base64

# ======================== CONFIG ==========================
# 🔑 Set your API keys here
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# ======================== SETUP ===========================
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# ======================== FUNCTIONS =======================
def describe_outfit(image_bytes):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        response = model.generate_content([
            "Describe the outfit in this image in detail. Focus on fashion style, vibe, and color.",
            image
        ])
        return response.text
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

def get_song_suggestion(description):
    prompt = f"""
    Suggest a *real* Spotify song (not made up) that fits the vibe of this outfit description:

    {description}

    Return only in this format:
    Song: <song name>
    Artist: <artist name>
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def extract_song_info(text):
    try:
        lines = text.splitlines()
        song_line = next(line for line in lines if line.lower().startswith("song"))
        artist_line = next(line for line in lines if line.lower().startswith("artist"))
        song_name = song_line.split(":", 1)[1].strip()
        artist_name = artist_line.split(":", 1)[1].strip()
        return song_name, artist_name
    except:
        return None, None

def search_spotify_track(song_name, artist_name):
    query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=query, type="track", limit=1)
    if results["tracks"]["items"]:
        return results["tracks"]["items"][0]
    return None

def audio_player_html(preview_url):
    if not preview_url:
        return "<p>No preview available.</p>"
    return f"""
    <audio controls autoplay>
        <source src="{preview_url}" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
    """

# ======================== UI THEME ========================
st.set_page_config(page_title="Fashion2Music 🎧", layout="centered", page_icon="🧥")
custom_css = """
<style>
body {
    background-color: #191414;
    color: white;
}
.css-18e3th9 {
    background: linear-gradient(to right, #1db954, #191414);
    color: white;
    box-shadow: 0 0 20px #1db954;
}
.css-1d391kg, .css-1v0mbdj, .stFileUploader {
    background-color: #121212;
    border-radius: 10px;
    color: white;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ======================== APP ============================
st.title("👗 Fashion to Music Recommender 🎶")
st.markdown("Upload a picture of your outfit, and we'll recommend a Spotify track that matches the vibe.")

uploaded_file = st.file_uploader("Upload your outfit image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Outfit", use_column_width=True)

    with st.spinner("🎨 Generating outfit description..."):
        image_bytes = uploaded_file.read()
        img_desc = describe_outfit(image_bytes)
    st.markdown(f"**🧥 Outfit Description:** {img_desc}")

    with st.spinner("🎵 Finding the perfect song..."):
        suggestion = get_song_suggestion(img_desc)
        song_name, artist_name = extract_song_info(suggestion)

        if not song_name or not artist_name:
            st.error("Couldn't parse the song suggestion. Try again.")
        else:
            st.markdown(f"**🎧 Recommended Song:** {song_name} by {artist_name}")
            track = search_spotify_track(song_name, artist_name)

            if track:
                preview_url = track.get("preview_url")
                spotify_url = track.get("external_urls", {}).get("spotify")
                st.markdown(audio_player_html(preview_url), unsafe_allow_html=True)
                if spotify_url:
                    st.markdown(f"🔗 [Open in Spotify]({spotify_url})")
            else:
                st.warning("Couldn't find this song on Spotify.")

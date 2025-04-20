import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 🔑 Set your API keys here
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# 🧠 Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# 🎧 Configure Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# 🏠 Streamlit App UI
st.title("🎨 Fashion Vibe → 🎧 Music Match")
st.markdown("Upload an outfit and get a music recommendation that fits your vibe!")

uploaded_img = st.file_uploader("Upload your outfit image", type=["jpg", "jpeg", "png"])

if uploaded_img:
    st.image(uploaded_img, caption="Your outfit", use_column_width=True)
    with st.spinner("Analyzing outfit and finding your vibe..."):

        # 📤 Prepare image for Gemini
        img_bytes = uploaded_img.read()
        image_part = {
            "mime_type": uploaded_img.type,
            "data": img_bytes
        }

        # 🤖 Ask Gemini for fashion analysis and song vibe
        prompt = (
            "You are a fashion and music expert. Analyze the outfit in this image, "
            "describe its style and vibe, and recommend a song (include name and artist) "
            "that matches the vibe. Format it like:\n"
            "🧥 Outfit Description: ...\n🎵 Recommended Song: ..."
        )

        try:
            response = model.generate_content([prompt, image_part], stream=False)
            output_text = response.text
            st.markdown(output_text)

            # 🎯 Extract song name and artist (basic parsing)
            if "🎵 Recommended Song:" in output_text:
                song_line = output_text.split("🎵 Recommended Song:")[-1].strip()
                st.markdown("🔍 Searching for song preview...")

                # 🔍 Search in Spotify
                results = sp.search(q=song_line, type="track", limit=1)
                tracks = results.get('tracks', {}).get('items', [])

                if tracks:
                    track = tracks[0]
                    song_name = track['name']
                    artist = track['artists'][0]['name']
                    preview_url = track['preview_url']
                    track_url = track['external_urls']['spotify']

                    st.markdown(f"**{song_name}** by *{artist}*")
                    st.markdown(f"[🔗 Listen on Spotify]({track_url})")

                    if preview_url:
                        st.audio(preview_url, format="audio/mp3")
                    else:
                        st.warning("Preview not available for this track.")
                else:
                    st.error("Couldn't find this song on Spotify.")
            else:
                st.warning("Couldn't parse the song from the response.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

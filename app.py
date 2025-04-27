import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
from dotenv import load_dotenv

load_dotenv()

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
            "that matches the vibe. DO NOT GIVE ANY OTHER EXTRA INFO LIKE VERSIONS.\n\n"
            "Requirements:\n"
            "- The song must be available on Spotify.\n"
            "- Format strictly like below (in separate lines):\n"
            "🧥 Outfit Description: ...\n"
            "🎵 Recommended Song: <Song Name>\n"
            "👤 Artist: <Artist Name>"
        )
        try:
            response = model.generate_content([prompt, image_part], stream=False)
            output_text = response.text
            st.markdown(output_text)

            # ✅ Use regex to extract exact song name and artist
            song_match = re.search(r'🎵 Recommended Song:\s*(.+)', output_text)
            artist_match = re.search(r'👤 Artist:\s*(.+)', output_text)

            if song_match and artist_match:
                song_name = song_match.group(1).strip()
                artist_name = artist_match.group(1).strip()
                query = f"track:{song_name} artist:{artist_name}"

                st.markdown(f"🔍 Searching for: **{song_name}** by *{artist_name}*")

                results = sp.search(q=query, type="track", limit=1)
                tracks = results.get('tracks', {}).get('items', [])

                if tracks:
                    track = tracks[0]
                    preview_url = track['preview_url']
                    track_url = track['external_urls']['spotify']

                    st.markdown(f"**{track['name']}** by *{track['artists'][0]['name']}*")
                    st.markdown(f"[🔗 Listen on Spotify]({track_url})")

                    if preview_url:
                        st.audio(preview_url, format="audio/mp3")
                    else:
                        st.warning("Preview not available for this track.")
                else:
                    st.error("❌ Couldn't find this song on Spotify.")
            else:
                st.warning("⚠️ Couldn't extract song name or artist from the response.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

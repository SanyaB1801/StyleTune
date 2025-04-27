import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
from dotenv import load_dotenv
import os
import time

# 🔑 Load API keys
load_dotenv()
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
st.set_page_config(page_title="Fashion Vibe → Music Match", page_icon="🎧")
st.title("🎨 Fashion Vibe → 🎧 Music Match")
st.markdown("Upload your outfit and get a **music recommendation** that fits your vibe! ✨")

with st.expander("ℹ️ About This App"):
    st.write("""
        Welcome to **Fashion Vibe → Music Match**!  
        1. Upload an image of your outfit.  
        2. AI analyzes your fashion style and vibe.  
        3. Get a perfect song recommendation you can vibe to! 🎵
    """)

uploaded_img = st.file_uploader("📸 Upload your outfit image", type=["jpg", "jpeg", "png"])

if uploaded_img:
    st.subheader("👕 Your Uploaded Outfit")

    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_img, caption="Your outfit", use_container_width=True)

    with col2:
        with st.spinner("Analyzing outfit and matching your music vibe... 🎶"):
            progress_bar = st.progress(0)
            for percent in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent + 1)

            # 📤 Prepare image for Gemini
            img_bytes = uploaded_img.read()
            image_part = {
                "mime_type": uploaded_img.type,
                "data": img_bytes
            }

            # 🤖 Fashion + Music Analysis Prompt
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

                # ✅ Use regex to extract fields
                outfit_desc_match = re.search(r'🧥 Outfit Description:\s*(.+)', output_text)
                song_match = re.search(r'🎵 Recommended Song:\s*(.+)', output_text)
                artist_match = re.search(r'👤 Artist:\s*(.+)', output_text)

                if outfit_desc_match and song_match and artist_match:
                    outfit_description = outfit_desc_match.group(1).strip()
                    song_name = song_match.group(1).strip()
                    artist_name = artist_match.group(1).strip()

                    # 🎯 Display fashion vibe
                    st.success("✨ Outfit & Music Vibe Found!")

                    with st.container():
                        st.markdown(
                            f"""
                            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
                                <h4>🧥 Outfit Description</h4>
                                <p style="color: #333;">{outfit_description}</p>
                                <h4>🎵 Recommended Song</h4>
                                <p><strong>{song_name}</strong> by *{artist_name}*</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # 🔍 Search Spotify
                    query = f"{song_name} {artist_name}"
                    results = sp.search(q=query, type="track", limit=1)
                    tracks = results.get('tracks', {}).get('items', [])

                    if tracks:
                        track = tracks[0]
                        preview_url = track['preview_url']
                        track_url = track['external_urls']['spotify']
                        album_art_url = track['album']['images'][0]['url']

                        st.markdown("## 🎶 Listen to Your Vibe")

                        # Album art + song info
                        col3, col4 = st.columns([1, 2])
                        with col3:
                            # Clickable album art
                            st.markdown(
                                f"""
                                <a href="{track_url}" target="_blank">
                                    <img src="{album_art_url}" alt="Album Art" style="width:200px; border-radius:10px; margin-top:10px;">
                                </a>
                                """,
                                unsafe_allow_html=True
                            )
                        with col4:
                            # Song name and artist nicely
                            st.markdown(f"<h4>{track['name']} by {track['artists'][0]['name']}</h4>", unsafe_allow_html=True)
                            # Listen on Spotify link (optional, because image is now clickable)
                            st.markdown(f"[🔗 Listen on Spotify]({track_url})")

                        if preview_url:
                            st.audio(preview_url, format="audio/mp3")
                        else:
                            st.warning("Preview not available for this track.")

                    else:
                        st.error("❌ Couldn't find this song on Spotify.")
                else:
                    st.warning("⚠️ Couldn't extract outfit or song details correctly. Try a different image!")

            except Exception as e:
                st.error(f"❌ Error: {e}")

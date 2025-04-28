import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageEnhance
import io
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
from dotenv import load_dotenv
import os
import time
import pandas as pd

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
st.set_page_config(page_title="StyleTune", page_icon="🎧")
st.title("StyleTune 🎧")
st.markdown("Upload your outfit and get a **music recommendation** that fits your vibe! ✨")
st.write("""
        Welcome to **StyleTune**!  
        1. Upload an image of your outfit.  
        2. AI analyzes your fashion style and vibe.  
        3. Get a perfect song recommendation you can vibe to! 🎵
    """)

# --- Session State ---
if "output" not in st.session_state:
    st.session_state.output = None
if "edited_image" not in st.session_state:
    st.session_state.edited_image = None
if "suggested_edits" not in st.session_state:
    st.session_state.suggested_edits = []
if "outfit_description" not in st.session_state:
    st.session_state.outfit_description = ""
if "song_name" not in st.session_state:
    st.session_state.song_name = ""
if "artist_name" not in st.session_state:
    st.session_state.artist_name = ""
if "track" not in st.session_state:
    st.session_state.track = None

# Upload image and enter vibe
uploaded_img = st.file_uploader("📸 Upload your outfit image", type=["jpg", "jpeg", "png"])
selected_vibe = st.text_input("🎧 What vibe are you feeling today? (optional)", value="")

# --- Generate Button ---
generate_button = st.button("✨ Generate Music & Vibe", disabled=not uploaded_img)

# inside your generate_button block:

if generate_button and uploaded_img:
    st.subheader("👕 Your Uploaded Outfit")
    st.image(uploaded_img, caption="Your outfit", use_container_width=True)

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

        # ✍️ Updated prompt that includes user-written vibe
        prompt = (
            f"You are a fashion and photography expert. Analyze the outfit in this image, "
            f"describe its style and vibe, recommend a song (include name and artist), "
            f"and suggest potential edits to enhance the image. "
            f"The user is feeling a '{selected_vibe}' vibe today, so make sure the song matches this vibe. "
            f"The edits can include adjustments to saturation, contrast, brightness, sharpness, etc. "
            f"Format the output exactly like this:\n\n"
            "🧥 Outfit Description: ...\n"
            "🎵 Recommended Song: <Song Name>\n"
            "👤 Artist: <Artist Name>\n"
            "🎨 Suggested Edits: <comma-separated edits>"
        )

        try:
            response = model.generate_content([prompt, image_part], stream=False)
            output_text = response.text
            st.session_state.output = output_text

            # ✅ Extract fields
            outfit_desc_match = re.search(r'🧥 Outfit Description:\s*(.+)', output_text)
            song_match = re.search(r'🎵 Recommended Song:\s*(.+)', output_text)
            artist_match = re.search(r'👤 Artist:\s*(.+)', output_text)
            edits_match = re.search(r'🎨 Suggested Edits:\s*(.+)', output_text)

            if outfit_desc_match and song_match and artist_match:
                st.session_state.outfit_description = outfit_desc_match.group(1).strip()
                st.session_state.song_name = song_match.group(1).strip()
                st.session_state.artist_name = artist_match.group(1).strip()
                st.session_state.suggested_edits = edits_match.group(1).strip().split(',')

                # 🔍 Search Spotify
                query = f"{st.session_state.song_name} {st.session_state.artist_name}"
                results = sp.search(q=query, type="track", limit=1)
                tracks = results.get('tracks', {}).get('items', [])

                if tracks:
                    st.session_state.track = tracks[0]
                else:
                    st.session_state.track = None
            else:
                st.warning("⚠️ Couldn't extract outfit or song details correctly. Try a different image!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Now when showing album art:

if st.session_state.output:
    st.success("✨ Outfit & Music Vibe Found!")

    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
            <h4>🧥 Outfit Description</h4>
            <p style="color: #333;">{st.session_state.outfit_description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.track:
        track = st.session_state.track
        preview_url = track['preview_url']
        track_url = track['external_urls']['spotify']
        album_art_url = track['album']['images'][0]['url']

        st.markdown("## 🎶 Listen to Your Vibe")

        # 🔗 Clickable album art leading to Spotify
        st.markdown(f"[![Album Art]({album_art_url})]({track_url})", unsafe_allow_html=True)

        if preview_url:
            st.audio(preview_url, format="audio/mp3")
        else:
            st.warning(f"Click to listen to {st.session_state.song_name} by {st.session_state.artist_name} on Spotify!")
    else:
        st.error("❌ Couldn't find this song on Spotify.")

    # 🎯 Feedback shown ONLY after track is found
    st.subheader("⭐ Rate Your Recommendation")

    if "rating" not in st.session_state:
        st.session_state.rating = 0

    cols = st.columns(5)
    for i, col in enumerate(cols):
        if col.button(f"{i+1} ⭐"):
            st.session_state.rating = i + 1

    if st.session_state.rating > 0:
        st.success(f"Thanks for rating {st.session_state.rating} star(s)! ⭐")

        # Save feedback
        feedback_data = {
            "Outfit Description": [st.session_state.outfit_description],
            "Selected Vibe": [selected_vibe],
            "Recommended Song": [st.session_state.song_name],
            "Artist": [st.session_state.artist_name],
            "Rating": [st.session_state.rating]
        }
        feedback_df = pd.DataFrame(feedback_data)
        feedback_file = "feedback_database.csv"

        try:
            existing_df = pd.read_csv(feedback_file)
            updated_df = pd.concat([existing_df, feedback_df], ignore_index=True)
        except FileNotFoundError:
            updated_df = feedback_df

        updated_df.to_csv(feedback_file, index=False)
        st.success("✅ Your feedback has been recorded successfully!")

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

uploaded_img = st.file_uploader("📸 Upload your outfit image", type=["jpg", "jpeg", "png"])

selected_vibe = st.text_input("🎧 What vibe are you feeling today?")

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
                "You are a fashion and photography expert. Analyze the outfit in this image, "
                "describe its style and vibe, recommend a song (include name and artist), "
                "and suggest potential edits to enhance the image. The edits can include adjustments "
                "to saturation, contrast, brightness, sharpness, or any other photographic enhancement "
                "that would match the outfit's vibe. Do not give extra information or instructions."
                "The values of the parameters in suggested edits must lie between 0.00 - 2.00 where 1.00 is no change."
                "Format the output as follows:\n\n"
                "🧥 Outfit Description: ...\n"
                "🎵 Recommended Song: <Song Name>\n"
                "👤 Artist: <Artist Name>\n"
                "🎨 Suggested Edits description in one line: ... "
                "🎨Brightness=<value>"
                "🎨Saturation=<value>"
                "🎨Sharpness=<value>"
                "🎨Contrast=<value>"
            )
            try:
                response = model.generate_content([prompt, image_part], stream=False)
                output_text = response.text

                # ✅ Use regex to extract fields
                outfit_desc_match = re.search(r'🧥 Outfit Description:\s*(.+)', output_text)
                song_match = re.search(r'🎵 Recommended Song:\s*(.+)', output_text)
                artist_match = re.search(r'👤 Artist:\s*(.+)', output_text)
                edits_match = re.search(r'🎨 Suggested Edits description in one line:\s*(.+)', output_text)
                brightness_match = re.search(r'🎨Brightness\s*([0-2](?:\.[0-9]{1,2})?)', output_text)
                saturation_match = re.search(r'🎨Saturation\s*([0-2](?:\.[0-9]{1,2})?)', output_text)
                sharpness_match = re.search(r'🎨Sharpness\s*([0-2](?:\.[0-9]{1,2})?)', output_text)
                contrast_match = re.search(r'🎨Contrast\s*([0-2](?:\.[0-9]{1,2})?)', output_text)

                if outfit_desc_match and song_match and artist_match and edits_match and brightness_match and saturation_match and sharpness_match and contrast_match:
                    outfit_description = outfit_desc_match.group(1).strip()
                    song_name = song_match.group(1).strip()
                    artist_name = artist_match.group(1).strip()
                    suggested_edits = edits_match.group(1).strip()
                    brightness_value = float(brightness_match.group(1))
                    saturation_value = float(saturation_match.group(1))
                    sharpness_value = float(sharpness_match.group(1))
                    contrast_value = float(contrast_match.group(1))

                    # 🎯 Display fashion vibe
                    st.success("✨ Outfit & Music Vibe Found!")

                    with st.container():
                        st.markdown(
                            f"""
                            <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
                                <h4>🧥 Outfit Description</h4>
                                <p style="color: #333;">{outfit_description}</p>
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
                            # Song name and artist only (no separate link)
                            st.markdown(f"<h4>{track['name']} by {track['artists'][0]['name']}</h4>", unsafe_allow_html=True)
                    else:
                        st.error("❌ Couldn't find this song on Spotify.")
                else:
                    st.warning("⚠️ Couldn't extract outfit or song details correctly. Try a different image!")

            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    st.subheader("🎨 Suggested Edits for Your Photo")
    st.write("suggested_edits")
    
    # Ask user to proceed with edits
    proceed = st.button("Proceed with Edits")
    
    if proceed:
        # Apply the edits to the image
        image = Image.open(uploaded_img)
    
        # Apply saturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation_value)
        # Apply contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast_value)
        #Apply brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness_value)
        #Apply sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(sharpness_value)
    
        st.image(image, caption="Edited Image", use_container_width=True)


    # Add after displaying album art + song
    st.subheader("⭐ Rate Your Recommendation")
    
    # Initialize session state for rating if not already set
    if "rating" not in st.session_state:
        st.session_state.rating = 0
    
    # Create 5 clickable stars
    cols = st.columns(5)
    for i, col in enumerate(cols):
        if col.button(f"{i+1} ⭐"):
            st.session_state.rating = i + 1
    
    # After clicking a star
    if st.session_state.rating > 0:
        st.success(f"Thanks for rating {st.session_state.rating} star(s)! ⭐")
    
        # Save the feedback
        feedback_data = {
            "Outfit Description": [outfit_description],
            "Selected Vibe": [selected_vibe],
            "Recommended Song": [song_name],
            "Artist": [artist_name],
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


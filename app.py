import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import base64
import requests
import time
import random
from dotenv import load_dotenv
import os
from io import BytesIO
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Check if API keys are present
if not GEMINI_API_KEY or not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    st.error("API keys are missing. Please check your .env file.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

# Spotify API Authentication
def authenticate_spotify(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data, auth=(client_id, client_secret))
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

access_token = authenticate_spotify(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

def search_spotify_track(query, access_token):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": query, "type": "track", "limit": 1}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        items = response.json().get("tracks", {}).get("items", [])
        if items:
            track = items[0]
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            preview_url = track.get("preview_url")
            external_url = track["external_urls"]["spotify"]
            return track_name, artist_name, preview_url, external_url
    return None, None, None, None

def get_gemini_suggestions(image_data):
    prompt = (
        "This is an image uploaded by the user. "
        "Suggest 3 minor but meaningful edits to enhance the image. "
        "Be specific (e.g., 'increase brightness', 'add slight vignette', 'sharpen details'). "
        "Respond with a numbered list only, no extra words."
    )
    try:
        response = model.generate_content([prompt, image_data])
        suggestions_text = response.text
        suggestions = [line.split('. ', 1)[1] for line in suggestions_text.split('\n') if '. ' in line]
        return suggestions
    except Exception as e:
        print("Error with Gemini API:", e)
        return []

def apply_edit(image, edit, value=None):
    if 'brightness' in edit.lower() and value:
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(value)
    elif 'contrast' in edit.lower() and value:
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(value)
    elif 'sharpness' in edit.lower() and value:
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(value)
    elif 'vignette' in edit.lower():
        vignette = Image.new('L', image.size, 0)
        for x in range(image.size[0]):
            for y in range(image.size[1]):
                vignette.putpixel((x, y), int(255 * (1 - ((x - image.size[0]/2)**2 + (y - image.size[1]/2)**2) / (image.size[0]*image.size[1]/4))))
        vignette = vignette.resize(image.size)
        return Image.composite(image, ImageOps.colorize(vignette, (0,0,0), (0,0,0)), vignette)
    else:
        return image  # No edit applied

# Streamlit UI
st.set_page_config(page_title="StyleTune 🎵👗", page_icon="🎵")

st.title("🎵👗 StyleTune: Match Your Look to a Tune!")

uploaded_img = st.file_uploader("Upload your outfit photo 📸", type=["jpg", "jpeg", "png"])

if uploaded_img:
    image = Image.open(uploaded_img)
    st.image(image, caption="Your Uploaded Outfit", use_column_width=True)

    with st.spinner('Analyzing your photo...'):
        time.sleep(1)  # Small delay for better UX
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode()
        image_data = {"mime_type": "image/jpeg", "data": img_b64}
        suggested_edits = get_gemini_suggestions(image_data)

    if suggested_edits:
        st.subheader("🎨 Suggested Edits for Your Photo")

        for edit in suggested_edits:
            st.markdown(f"- {edit}")

        if st.button("✨ Proceed with Edits"):
            edited_image = image.copy()
            for edit in suggested_edits:
                if 'brightness' in edit.lower():
                    brightness = st.slider('Adjust Brightness', 0.5, 2.0, 1.0)
                    edited_image = apply_edit(edited_image, edit, brightness)
                elif 'contrast' in edit.lower():
                    contrast = st.slider('Adjust Contrast', 0.5, 2.0, 1.0)
                    edited_image = apply_edit(edited_image, edit, contrast)
                elif 'sharpness' in edit.lower():
                    sharpness = st.slider('Adjust Sharpness', 0.5, 2.0, 1.0)
                    edited_image = apply_edit(edited_image, edit, sharpness)
                elif 'vignette' in edit.lower():
                    edited_image = apply_edit(edited_image, edit)

            st.image(edited_image, caption="Edited Photo", use_column_width=True)

    st.subheader("🎵 Your Recommended Track")
    with st.spinner('Finding the perfect track for you...'):
        time.sleep(0.5)
        random_keywords = ['fashion', 'style', 'confidence', 'cool', 'chill', 'energetic', 'mood']
        search_query = random.choice(random_keywords)
        track_name, artist_name, preview_url, external_url = search_spotify_track(search_query, access_token)

    if track_name:
        st.success(f"**{track_name}** by *{artist_name}*")
        if preview_url:
            st.audio(preview_url, format='audio/mp3')
        st.markdown(f"[Listen on Spotify]({external_url})")
    else:
        st.error("Couldn't find a track. Please try again later.")

    st.subheader("⭐ Rate Your Experience")
    rating = st.slider('How would you rate this suggestion?', 1, 5, 3)

    if st.button("Submit Rating"):
        with st.spinner('Saving your feedback...'):
            time.sleep(0.5)
            # Here you could save rating to a database or file
            st.success(f"Thanks for rating us {rating} stars! 🌟")

else:
    st.info("👆 Upload an image to get started!")


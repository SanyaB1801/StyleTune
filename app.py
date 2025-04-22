import streamlit as st
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image
import random
import re
from dotenv import load_dotenv
load_dotenv()
import os

# === Setup ===
st.set_page_config(page_title="Fashion Vibe → Music Match", layout="centered")

# === Spotify Auth ===
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

# === Label Encoder (same order as training) ===
label_list = ['Blazer', 'Dress', 'Hoodie', 'Jacket', 'Jeans', 'Kurta', 'Shorts', 'Skirt', 'Sweater', 'Tshirt']
inv_label_encoder = {i: name for i, name in enumerate(label_list)}

# === Fashion → Genre Mapping ===
fashion_to_genre = {
    "Blazer": "smooth jazz", "Dress": "lofi beats", "Jeans": "indie pop",
    "Jacket": "rock", "Kurta": "indian classical", "Shorts": "tropical house",
    "Skirt": "dream pop", "Sweater": "acoustic", "Tshirt": "pop", "Hoodie": "trap"
}

# === Fetch Spotify Songs ===
def fetch_spotify_tracks(genre):
    results = sp.search(q=genre, limit=20, type='track', market='US')
    tracks = results['tracks']['items']
    return [(t['name'], t['artists'][0]['name'], t['external_urls']['spotify']) for t in tracks]

# === Load Model ===
@st.cache_resource
def load_model():
    base_model = MobileNetV2(include_top=False, input_shape=(128,128,3), weights='imagenet')
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    predictions = Dense(len(label_list), activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=predictions)

    # Load trained weights (path to your trained weights file)
    model.load_weights("mobilenet_fashion_weights.h5")
    return model

model = load_model()

# === Image Prediction ===
def predict_fashion(img_pil):
    img = img_pil.resize((128, 128))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    pred = np.argmax(model.predict(img_array), axis=1)[0]
    return inv_label_encoder[pred]

# === UI ===
st.title("👗 Fashion Vibe → Music Match 🎶")
st.markdown("Upload an outfit photo to discover the music that matches your fashion vibe!")

uploaded_img = st.file_uploader("Upload your fashion image", type=['jpg', 'jpeg', 'png'])

if uploaded_img:
    img_pil = Image.open(uploaded_img).convert("RGB")
    st.image(img_pil, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing fashion style..."):
        fashion = predict_fashion(img_pil)
        genre = fashion_to_genre.get(fashion, "lofi beats")
        song_list = fetch_spotify_tracks(genre)
        song, artist, link = random.choice(song_list)

    st.markdown(f"### 🎯 Style Detected: **{fashion}**")
    st.markdown(f"### 🎵 Genre Vibe: **{genre}**")
    st.markdown(f"### 🎧 Listening Suggestion:")
    st.markdown(f"- **{song}** by *{artist}*")
    st.markdown(f"[🔗 Listen on Spotify]({link})")

    st.audio(link.replace("open.", "p.scdn.co/mp3-preview/").replace("/track/", "/"), format="audio/mp3")

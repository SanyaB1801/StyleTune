import streamlit as st
import requests
from PIL import Image
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import io

# Define your Spotify credentials
SPOTIPY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIPY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"

# Setup Spotipy
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Define the vibe features
vibe_features = {
    "lofi beats": {"valence": (0.4, 0.7), "energy": (0.2, 0.4)},
    "chill indie": {"valence": (0.5, 0.8), "acousticness": (0.5, 1.0)},
    "confident jazz": {"valence": (0.5, 0.9), "instrumentalness": (0.7, 1.0)},
    # Add more vibes as needed
}

# Load the trained model for fashion style classification (pre-trained CNN model)
model = tf.keras.models.load_model('fashion_style_model.h5')  # Make sure to provide your model path

# Function to process image and predict fashion style
def process_image(image):
    img = image.resize((128, 128))  # Resize to match the model input size
    img_array = img_to_array(img) / 255.0  # Normalize image
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Function to recommend a song based on fashion style
def recommend_song(vibe):
    if vibe not in vibe_features:
        return None
    
    target_features = vibe_features[vibe]
    results = sp.recommendations(seed_genres=[vibe], limit=3, target_valence=target_features.get("valence", (0, 1))[1],
                                 target_energy=target_features.get("energy", (0, 1))[1], target_acousticness=target_features.get("acousticness", (0, 1))[1])

    if results['tracks']:
        track_uri = results['tracks'][0]['uri']
        return track_uri
    return None

# Streamlit UI
st.title("Fashion Style to Music Recommendation")
st.write("Upload an image of your outfit, and we'll suggest a song to match your vibe!")

# Upload image
uploaded_image = st.file_uploader("Choose an image...", type="jpg")

if uploaded_image:
    # Process image and predict fashion style
    image = Image.open(uploaded_image)
    image_array = process_image(image)
    
    # Predict fashion style (replace with your model)
    predicted_style = model.predict(image_array)  # You should map this to actual styles
    vibe = "lofi beats"  # Replace this with the actual prediction logic based on your model output

    st.image(image, caption="Uploaded Image", use_column_width=True)
    st.write(f"Predicted Fashion Style: {vibe}")

    # Recommend a song
    song_uri = recommend_song(vibe)
    if song_uri:
        track_url = f"https://open.spotify.com/track/{song_uri.split(':')[2]}"
        st.write("Recommended song for your vibe:")
        st.markdown(f"[Listen on Spotify]({track_url})")
    else:
        st.write("Sorry, no song recommendations available at the moment.")

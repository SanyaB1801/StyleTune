# StyleTune 🎧

**StyleTune** is a web application that matches your fashion style to the perfect music vibe! Upload an image of your outfit, select the vibe you're feeling, and get a personalized song recommendation.

---

## Features
- **Outfit Analysis:** Upload an image of your outfit, and our AI will analyze its style and vibe.
- **Music Recommendation:** Based on your outfit and selected vibe, the AI recommends a song from Spotify that fits the mood.
- **Rating System:** Rate the song recommendation with a 1-5 star system to provide feedback.
- **Spotify Integration:** Directly play the song preview on the app or access it on Spotify.

## Technologies Used
- **Streamlit:** For creating the web app interface.
- **Google Gemini AI:** To analyze the outfit and generate song recommendations.
- **Spotify API:** To fetch song details and allow users to listen to previews.
- **Pandas:** To manage and store feedback data in a CSV file.
- **Python:** The core programming language for backend logic.

## Installation & Setup

### Prerequisites
- Python 3.7+
- [Spotify Developer Account](https://developer.spotify.com/) to get API credentials.
- [Google Gemini API Access](https://developers.google.com/genai/) for fashion and music analysis.

### Steps
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/style-tune.git
   cd style-tune
   ```

2. **Install Dependencies:**
   It's recommended to use a virtual environment to manage dependencies.
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Set Up API Keys:**
   - Create a `.env` file in the root directory and add the following keys:
     ```
     GEMINI_API_KEY=<Your_Gemini_API_Key>
     SPOTIFY_CLIENT_ID=<Your_Spotify_Client_ID>
     SPOTIFY_CLIENT_SECRET=<Your_Spotify_Client_Secret>
     ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

5. **Access the App:**
   Open your browser and navigate to `http://localhost:8501` to use the app.

## Usage
1. **Upload Outfit:** Upload an image of your outfit. The AI will analyze the style and vibe.
2. **Select Vibe:** Type in the vibe you're feeling today (e.g., "chill," "energetic," "romantic").
3. **Get Music Recommendation:** Based on the analysis, a song will be recommended to match your outfit and vibe.
4. **Rate the Recommendation:** After hearing the song, rate it from 1-5 stars.

## Feedback Database
- All ratings and feedback are stored in a `feedback_database.csv` file. The app appends new feedback entries, which include:
  - **Outfit Description**
  - **Selected Vibe**
  - **Recommended Song**
  - **Artist**
  - **Rating**

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-xyz`).
3. Commit your changes (`git commit -am 'Add feature xyz'`).
4. Push to the branch (`git push origin feature-xyz`).
5. Create a new Pull Request.

### Acknowledgments
- Thanks to the [Spotify API](https://developer.spotify.com/) for enabling seamless song integration.
- Powered by the [Google Gemini AI](https://developers.google.com/genai/) for fashion and vibe analysis.

---

#### **Enjoy styling your outfits with the perfect music vibe! 🎶** 
```

### Explanation:
- **Introduction:** Gives a brief about the project.
- **Technologies Used:** Lists the technologies and services used in the project.
- **Installation & Setup:** Provides a clear guide to setting up the project, including dependencies, API key configuration, and running the app.
- **Usage:** Describes how the app works.
- **Feedback Database:** Describes how feedback is stored.
- **License & Contributing:** Information about contributing to the project and licensing.

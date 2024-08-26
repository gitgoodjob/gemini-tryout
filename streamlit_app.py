import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import os
import tempfile

# Set up the Streamlit app
st.title("Multilingual Gemini Chatbot with Voice Support")

# Create a form to input the Gemini API Key
with st.form("Enter API Key"):
    API_KEY = st.text_input("Enter Gemini API Key")
    submit_api_key = st.form_submit_button("Submit")

if submit_api_key:
    try:
        genai.configure(api_key=API_KEY)
        st.success("API key configured successfully!")
    except Exception as e:
        st.error(f"Error configuring API key: {str(e)}")

model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize the speech recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Function to perform speech recognition
def speech_to_text(language_code):
    with sr.Microphone() as source:
        st.write("Listening... Speak now.")
        audio = recognizer.listen(source)
        st.write("Processing speech...")
    try:
        text = recognizer.recognize_google(audio, language=language_code)
        return text
    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand the audio.")
        return None
    except sr.RequestError:
        st.error("Sorry, there was an error processing your request.")
        return None

# Function to translate text
def translate_text(text, target_language):
    try:
        detection = translator.detect(text)
        translation = translator.translate(text, dest=target_language)
        return detection.lang, translation.text
    except Exception as e:
        st.warning(f"Translation error: {str(e)}. Returning original text.")
        return 'unknown', text

# Function to convert text to speech
def text_to_speech(text, language):
    try:
        tts = gTTS(text=text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.warning(f"Text-to-speech error: {str(e)}. Audio output not available.")
        return None

# Language selection
languages = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Chinese': 'zh-cn',
    'Hindi': 'hi',
    'Sanskrit': 'sa'
}
selected_language = st.selectbox("Select language", list(languages.keys()))

# Create a form to input the search query
with st.form("search_form"):
    input_method = st.radio("Choose input method", ("Text", "Voice"))
    if input_method == "Text":
        search_query = st.text_input("Enter your search query")
    else:
        if st.form_submit_button("Start Voice Input"):
            search_query = speech_to_text(languages[selected_language])
            if search_query:
                st.write(f"You said: {search_query}")
    submit_search = st.form_submit_button("Search")

# Main logic
if submit_search and search_query:
    try:
        # Detect the language of the input query
        detected_lang, _ = translate_text(search_query, 'en')
        st.info(f"Detected input language: {LANGUAGES.get(detected_lang, 'Unknown')}")

        # Translate query to English if not already in English
        if detected_lang != 'en':
            _, english_query = translate_text(search_query, 'en')
            st.info(f"Translated query to English: {english_query}")
        else:
            english_query = search_query

        # Generate response using the Gemini model
        response = model.generate_content(english_query)

        # Translate response back to selected language if not English
        if selected_language != 'English':
            _, translated_response = translate_text(response.text, languages[selected_language])
            st.info(f"Translated response to {selected_language}")
        else:
            translated_response = response.text

        # Display the response in a formatted box
        st.subheader("Response:")
        st.markdown(f"```\n{translated_response}\n```")

        # Generate audio for the response
        audio_file = text_to_speech(translated_response, languages[selected_language])
        if audio_file:
            st.audio(audio_file)
            # Clean up the temporary audio file
            os.unlink(audio_file)

    except Exception as e:
        st.error(f"Error generating or translating text: {str(e)}")

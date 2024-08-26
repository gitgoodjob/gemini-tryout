import streamlit as st
import google.generativeai as genai
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import os
import tempfile
import base64
import speech_recognition as sr
from io import BytesIO

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

# Initialize the translator
translator = Translator()

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

# Audio recording function
def record_audio():
    audio_bytes = st.session_state.get("audio_bytes", None)
    if audio_bytes:
        # Convert audio bytes to audio data
        audio_data = BytesIO(audio_bytes)
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_data) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language=languages[selected_language])
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I couldn't understand the audio.")
        except sr.RequestError:
            st.error("Sorry, there was an error processing your request.")
    return None

# JavaScript for microphone access
st.markdown("""
<script>
const toggleMic = () => {
    const micElem = document.getElementById('micButton');
    if (micElem.textContent === '🎙️ Start') {
        micElem.textContent = '🎙️ Stop';
        startRecording();
    } else {
        micElem.textContent = '🎙️ Start';
        stopRecording();
    }
}

let mediaRecorder;
let audioChunks = [];

const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });
        });
}

const stopRecording = () => {
    mediaRecorder.stop();
    mediaRecorder.addEventListener("stop", () => {
        const audioBlob = new Blob(audioChunks);
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
            const base64data = reader.result;
            Streamlit.setComponentValue(base64data);
        }
        audioChunks = [];
    });
}

const pushToTalk = (event) => {
    if (event.type === 'mousedown' || event.type === 'touchstart') {
        startRecording();
    } else if (event.type === 'mouseup' || event.type === 'touchend') {
        stopRecording();
    }
}
</script>
""", unsafe_allow_html=True)

# Microphone toggle button
st.markdown("""
<button id="micButton" onclick="toggleMic()">🎙️ Start</button>
""", unsafe_allow_html=True)

# Push-to-talk button
st.markdown("""
<button id="pushToTalkButton" onmousedown="pushToTalk(event)" onmouseup="pushToTalk(event)" ontouchstart="pushToTalk(event)" ontouchend="pushToTalk(event)">🎙️ Push to Talk</button>
""", unsafe_allow_html=True)

# Create a form to input the search query
with st.form("search_form"):
    search_query = st.text_input("Enter your search query")
    submit_search = st.form_submit_button("Search")

# Handle audio input
audio_bytes = st.session_state.get("audio_bytes", None)
if audio_bytes:
    audio_base64 = audio_bytes.split(",")[1]
    audio_data = base64.b64decode(audio_base64)
    st.session_state.audio_bytes = audio_data
    search_query = record_audio()
    if search_query:
        st.write(f"You said: {search_query}")

# Main logic
if submit_search or search_query:
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

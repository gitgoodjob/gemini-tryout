import streamlit as st
from transformers import LlamaModel, LlamaConfig
import google.generativeai as genai
import os


# Set up the Streamlit app
st.title("LLaMA Chatbot")
with st.form("Enter API Key"):
    API_KEY=st.text_input("Enter Gemini API Key")
    

# Create a form to input the search query
with st.form("search_form"):
    search_query = st.text_input("Enter your search query")
    submit_search = st.form_submit_button("Search")

# Create a container to display the model information
model_info = st.empty()

genai.configure(api_key=os.environ["API_KEY"]
# Load the LLaMA model
configuration = LlamaConfig()
model = LlamaModel(configuration)

# Function to generate text using the LLaMA model
def generate_text(query):
    return model(query, max_length=200)[0]["generated_text"]

# Main logic
if submit_search:
    search_results = generate_text(search_query)
    st.write(search_results)

# Display model information
model_info.write("Model: LLaMA 7B")

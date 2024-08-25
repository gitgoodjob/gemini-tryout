import streamlit as st
import google.generativeai as genai
import os

# Set up the Streamlit app
st.title("Gemini Chatbot")

# Create a form to input the Gemini API Key
with st.form("Enter API Key"):
    API_KEY = st.text_input("Enter Gemini API Key")
    submit_api_key = st.form_submit_button("Submit")

if submit_api_key:
    try:
        # Configure the Gemini API using the API key provided by the user
        genai.configure(api_key=API_KEY)
        st.success("API key configured successfully!")
    except Exception as e:
        st.error(f"Error configuring API key: {str(e)}")

model = genai.GenerativeModel("gemini-1.5-flash")

# Create a form to input the search query
with st.form("search_form"):
    search_query = st.text_input("Enter your search query")
    submit_search = st.form_submit_button("Search")

# Main logic
if submit_search:
    try:
        # Generating text using the Gemini model
        response = model.generate_content(search_query)
        
        # Display the response in a formatted box
        st.subheader("Response:")
        st.markdown(f"```\n{response.text}\n```")
    except Exception as e:
        st.error(f"Error generating text: {str(e)}")

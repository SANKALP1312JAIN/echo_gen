import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64
from difflib import SequenceMatcher
import uuid
import os
from st_audiorec import st_audiorec

# Initialize OpenAI client
def setup_openai_client(api_key):
    try:
        openai.api_key = api_key
        return openai
    except Exception as e:
        st.error("Failed to set up OpenAI client. Please check your API key.")
        return None

# Function to transcribe audio to text
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        response = openai.Audio.transcribe(
            model="whisper-1",  # Specify the Whisper model
            file=audio_file,
            language="en"  # Specify the language of the audio
        )
    return response["text"]

# Function to calculate similarity between two texts
def calculate_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

# Function to convert text to audio
def text_to_audio(client, text, audio_path):
    response = client.Audio.synthesize(model="tts-1", voice="echo", input=text)
    with open(audio_path, "wb") as f:
        f.write(response['data'])

def navigate_to_page(page_number):
    st.session_state.page = page_number

# Function to count existing recorded files for a user
def count_existing_audio_samples(user_directory):
    return len([f for f in os.listdir(user_directory) if f.startswith("audio_sample_") and f.endswith(".wav")])

# Function to generate text using ondemain.io's text generation API
def generate_dynamic_text(prompt):
    # Placeholder function - Replace with actual API integration code
    # Example: Sending prompt to the ondemain.io API and getting a response
    return f"Generated text based on: {prompt}"

# Main function
def main():
    st.title("💬 🎙️ Welcome to ECHO GEN...🎧")
    st.text(
        "This is an AI voice generating software.\n"
    )

    # User login: Enter username on the Home page
    if "username" not in st.session_state:
        st.session_state.username = None

    if st.session_state.username is None:
        username = st.text_input("Enter Username")
        
        if st.button("LOGIN"):
            st.session_state.username = username
            st.session_state.page = 1
            st.success("Login successful!")
            st.text("Please provide 5 voice samples by reading the given sentences.")
            
            # Set up user directory and record counter on login
            user_directory = f"audio_samples/{username}"
            if not os.path.exists(user_directory):
                os.makedirs(user_directory)
            
            # Initialize record counter based on existing recordings
            st.session_state.record_counter = count_existing_audio_samples(user_directory)
        
        return  # Do not proceed until user logs in

    # Initialize session state variables if they do not exist
    if "page" not in st.session_state:
        st.session_state.page = 1  # Set Home page as default (numerical representation)
    if "record_counter" not in st.session_state:
        st.session_state.record_counter = 0  # Initialize counter for About page

    # API Key and setup
    api_key = "cxs3IZBdeq23SLHzHNA_q91eaa2X8VFP6W6oi078IvzkWwPyvMLawSj2n75qv19yHy4G5jq2e2T3BlbkFJN8T003EeIDekI7xk2RTLnJFEebaPaACxUhY8RMKHDOhKiWR81zrQOJrkcw1jvkIN8Zyot0aQgA"
    client = setup_openai_client(api_key)

    # Set up columns for navigation buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("HOME"):
            navigate_to_page(1)

    with col2:
        if st.button("RECORD AUDIO SAMPLES"):
            navigate_to_page(2)

    with col3:
        if st.button("GENERATE YOUR VOICE"):
            navigate_to_page(3)

    # Generate user-specific directory
    user_directory = f"audio_samples/{st.session_state.username}"
    
    # List of prompts
    prompts = [
        "Hello, welcome to ECHO GEN!",
        "Please record your voice to create a custom voice profile.",
        "This is the third sample sentence for the voice model.",
        "Almost there, just one more after this!",
        "Thank you for providing your voice samples."
    ]

    # Display content based on the selected page
    if st.session_state.page == 1:
        st.write("Welcome to the Home Page!")
        increment = st.button("Proceed to Recording")
        if increment:
            navigate_to_page(2)

    elif st.session_state.page == 2:
        record_counter = st.session_state.record_counter
        if record_counter < len(prompts):
            prompt = prompts[record_counter]
            st.write(f"Sample {record_counter + 1}: {prompt}")

            # Record audio
            unique_key = f"audio_recorder_{record_counter}_{uuid.uuid4().hex}"
            wav_audio_data = st_audiorec()

            if wav_audio_data:
                audio_file = f"{user_directory}/audio_sample_{record_counter}.wav"
                with open(audio_file, "wb") as f:
                    f.write(wav_audio_data)
                st.success(f"Sample {record_counter + 1} recorded successfully!\nPlease click on reset to record next audio")
                st.session_state.record_counter += 1
            else:
                st.warning("No audio recorded. Please try again.")
            
        if st.session_state.record_counter == 5:
            st.success("All 5 voice samples have been recorded.")
            navigate_to_page(3)

    elif st.session_state.page == 3:
        if st.session_state.record_counter < 5:
            st.warning("Please record all 5 audio samples first.")
            navigate_to_page(2)
        else:
            st.text("Generating your custom voice model...")
            
            # Tabs for choosing between direct input or text generation
            tab1, tab2 = st.tabs(["Say as is", "Use Text Generation"])

            # Option 1: Direct input and voice generation
            with tab1:
                user_text = st.text_input("Enter the text you want to hear in your custom voice:")
                response_audio_file = f"{user_directory}/generated_audio_response.wav"

                if user_text and client:
                    try:
                        text_to_audio(client, user_text, response_audio_file)
                        st.audio(response_audio_file)
                        st.success("Generated voice has been played and saved successfully!")
                    except Exception as e:
                        st.error(f"An error occurred while generating voice: {e}")

            # Option 2: Dynamic text generation using ondemain.io API
            with tab2:
                prompt_text = st.text_input("Enter a prompt for text generation:")
                if prompt_text:
                    generated_text = generate_dynamic_text(prompt_text)
                    st.write(f"Generated Text: {generated_text}")

                    if client and generated_text:
                        try:
                            response_audio_file = f"{user_directory}/generated_audio_dynamic.wav"
                            text_to_audio(client, generated_text, response_audio_file)
                            st.audio(response_audio_file)
                            st.success("Generated voice from dynamic text has been played and saved successfully!")
                        except Exception as e:
                            st.error(f"An error occurred while generating voice from dynamic text: {e}")

if __name__ == "__main__":
    main()

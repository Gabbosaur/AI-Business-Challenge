import streamlit as st
import os
from groq import Groq
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Set up the Streamlit app
st.title("API Tester: Groq vs. Anthropic")

# Sidebar for API selection
api_choice = st.sidebar.selectbox("Choose an API", ["Groq API", "Anthropic API"])

# Input form in the main section
st.subheader("Enter your input for the API")
user_input = st.text_input("Input prompt or data:")

# Button to make API request
if st.button("Submit"):
    if user_input:
        # Define the output variable
        response_text = ""

        # Make the request based on the selected API
        if api_choice == "Groq API":
            my_groq_api_key = os.getenv("GROQ_API_KEY")
            client = Groq(
                api_key=my_groq_api_key,
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ],
                model="llama3-8b-8192",
            )
            response_text = chat_completion.choices[0].message.content


        elif api_choice == "Anthropic API":
            my_anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            client = Anthropic(
                api_key=my_anthropic_api_key
            )
            our_first_message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": user_input }
                ]
            )
            response_text = our_first_message.content[0].text

        # Display the response
        st.subheader("API Response")
        st.write(response_text)
    else:
        st.warning("Please enter input before submitting.")

import streamlit as st
import os
from groq import Groq
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# System prompt for the workout coach role
SYSTEM_PROMPT = "As a personal fitness coach specializing in calisthenics, your role is to design personalized workout plans tailored to individual clients. These plans should consider their unique goals, physical capabilities, time availability, and the equipment they have access to (such as parallettes, rings, pull-up bars, and parallel bars). The exercises should focus on improving strength, endurance, and flexibility, while maintaining a balance between challenge and attainability. You are also responsible for providing ongoing motivation and support. If a client mentions having less than 10 minutes per day, advise them on the need for more time to achieve effective results."

# Set up the Streamlit app
st.title("🏋️‍♂️ Your Personal Workout Coach 🤖")

# Sidebar for API selection
api_choice = st.sidebar.selectbox("API Selection", ["Groq API", "Anthropic API"])

# Input form in the main section
st.subheader("Input Data")

# User input fields for physical info, now more compact
with st.container():
    gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
    age = st.number_input("Age:", min_value=16, max_value=120, step=1, value=30)
    weight = st.number_input("Weight (kg):", min_value=30.0, step=1.0, value=70.0)
    height = st.number_input("Height (cm):", min_value=100.0, step=1.0, value=170.0)
    fitness_goals = st.text_input("Goals (e.g., lose weight):", "")
    user_input = st.text_input("Additional Comments (optional):", "")

# Personal fitness level
fitness_level = st.selectbox("Fitness Level:", ["Beginner", "Intermediate", "Advanced"])

# Fixed list of available equipment for selection
equipment_options = ["Parallettes", "Rings", "Pull-up Bar", "Parallel Bars", "Dumbbells", "Resistance Bands"]
equipment = st.multiselect("Equipment:", options=equipment_options)

# Time available input in a single-row layout
st.subheader("Time Available (min/day)")
days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
columns = st.columns(7)
time_available = {day: columns[i].number_input(f"{day}:", min_value=0, max_value=360, step=5) for i, day in enumerate(days_of_week)}

# Button to make API request
if st.button("Submit"):
    # Define the output variable
    response_text = ""

    # Prepare the user details as additional context
    user_details = (
        f"Age: {age}, Weight: {weight} kg, Height: {height} cm, "
        f"Goals: {fitness_goals}, Level: {fitness_level}, Gender: {gender}, "
        f"Equipment: {', '.join(equipment)}, Time Available: {time_available}"
    )

    # Combine the main user input and additional details if provided
    full_user_input = user_details
    if user_input:  # Only add additional comments if user_input is provided
        full_user_input += f"\n\nAdditional Comments:\n{user_input}"

    # Make the request based on the selected API
    if api_choice == "Groq API":
        my_groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=my_groq_api_key)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": full_user_input,
                }
            ],
            model="llama3-8b-8192",
        )
        response_text = chat_completion.choices[0].message.content

    elif api_choice == "Anthropic API":
        my_anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=my_anthropic_api_key)

        our_first_message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": full_user_input
                }
            ]
        )
        response_text = our_first_message.content[0].text

    # Display the response
    st.subheader("API Response")
    st.write(response_text)

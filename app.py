import streamlit as st
import os
import json
from groq import Groq
from anthropic import Anthropic
from dotenv import load_dotenv
from pdf_generator import main as pdf_generator

load_dotenv()

# System prompt for the workout coach role
SYSTEM_PROMPT = """As a personal fitness coach specializing in calisthenics, your role is to design personalized workout plans tailored to individual clients.
These plans should consider their unique goals, physical capabilities, time availability, and the equipment they have access to (such as parallettes, rings, pull-up bars, and parallel bars).
The exercises should focus on improving strength, endurance, and flexibility, while maintaining a balance between challenge and attainability. You are also responsible for providing ongoing motivation and support.\n\n
Don't put days of week together.
The response should have the following format:\n
WorkoutName: xxx\n\n
Goals: xxx\n\n
Level: xxx\n\n
Equipment: bullet point of available equipments\n\n
Time Available: bullet point of time available in minutes per day\n\n
Monday: list of set and reps\n\n
Tuesday: list of set and reps\n\n
Wednesday: list of set and reps\n\n
Thursday: list of set and reps\n\n
Friday: list of set and reps\n\n
Saturday: list of set and reps\n\n
Sunday: list of set and reps\n\n
Tips and Motivation: bullet point\n\n

At the end produce the same result in the following JSON format with delimiters called "___JSON___" :

{
  "workout_name": "xxxx",
  "workouts": [
    {
      "day_of_week": "xxx",
      "exercises": [
        {
          "name": name of the exercise,
          "sets": number of sets (string),
          "reps": number of reps (string),
          "tools": name the tool if required for the exercise,
          "comment": comments and tips about the exercise
        }
      ]
    }
  ],
  "tips": give tips and motivation
}
"""

def extract_before_and_json(input_text):
    # Split the text at "JSON: " and separate the before and after parts
    parts = input_text.split("___JSON___")

    # If "JSON: " is found, assign parts accordingly
    before_text = parts[0].strip()
    json_text = parts[1].strip() if len(parts) > 1 else None

    return before_text, json_text

# Set up the Streamlit app
st.title("🏋️‍♂️ Your Personal Workout Coach")

# Sidebar for API selection
api_choice = st.sidebar.selectbox("API Selection", ["Groq API", "Anthropic API"])

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
response_text = ""


# Button to make API request
if st.button("Submit"):

    # Validate each day's time
    invalid_days = [day for day, time in time_available.items() if 1 <= time <= 19]
    if invalid_days:
        st.error(f"Time for {', '.join(invalid_days)} is too low to be effective. Please provide at least 20 minutes or 0 for rest.")
    else:
        with st.spinner("Loading..."):  # Show the loading spinner
            if len(equipment) == 0:
                equipment = "No equipment"

            # Prepare the user details as additional context
            user_details = (
                f"Age: {age}, Weight: {weight} kg, Height: {height} cm, "
                f"Goals: {fitness_goals}, Level: {fitness_level}, Gender: {gender}, "
                f"Equipment: {equipment}, Time available in minutes: {time_available}"
            )
            # Combine the main user input and additional details if provided
            full_user_input = user_details
            if user_input:  # Only add additional comments if user_input is provided
                full_user_input += f"\n\nAdditional Comments:\n{user_input}"
                # print(full_user_input)
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
                    model="llama-3.1-8b-instant",
                    temperature=0,
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
        response, response_json = extract_before_and_json(response_text)

        st.write(response)

        st.info(response_json)

        # Save JSON data to a file
        output_file = os.path.join('data', 'workout_plan.json')
        # print("workout_json: " + response_json)
        parsed_json = json.loads(response_json)

        # Define the folder name
        folder_name = "data"

        # Check if the folder exists
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created.")
        else:
            print(f"Folder '{folder_name}' already exists.")

        # Save JSON data to file, creating it if it doesn't exist
        with open(output_file, 'w') as file:
            json.dump(parsed_json, file, indent=4)

        generated_pdf_path = pdf_generator(output_file)
        print(f"Workout plan saved to {output_file}")
        st.success(" Exported to PDF")

          # Create a download button for the PDF
        with open(generated_pdf_path, "rb") as f:
            pdf_data = f.read()
        
        st.download_button(
            label="Download Workout Plan PDF",
            data=pdf_data,
            file_name="your_workout_plan",
            mime='application/pdf',
            key='download_pdf'  # Unique key to avoid key collisions
        )

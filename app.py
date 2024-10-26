import streamlit as st
import os
import json
import re
from groq import Groq
from anthropic import Anthropic
from dotenv import load_dotenv
from pdf_generator import main as pdf_generator

load_dotenv()


# def parse_workout_plan(text):
#     # Split text into parts based on workout days
#     days = re.split(r"(?=\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b)", text.strip())
#     workout_plan = {}
    
#     for day in days:
#         # Extract the day name
#         day_match = re.match(r"(\w+)\s*\(.*\)", day)
#         if day_match:
#             day_name = day_match.group(1)
#             # Get exercises, ignoring initial lines before the exercises
#             exercises = re.findall(r"(?<=\n)[^\n]+", day)
            
#             daily_workout = {}
#             for exercise in exercises:
#                 exercise = exercise.strip()
#                 if ':' in exercise:
#                     exercise_name, details = exercise.split(':', 1)
#                     daily_workout[exercise_name.strip()] = details.strip()
#                 elif exercise:  # Only add if the line is not empty
#                     daily_workout[exercise] = "Rest day or specific activity not detailed."
            
#             workout_plan[day_name] = daily_workout
    
#     return workout_plan


# System prompt for the workout coach role
SYSTEM_PROMPT = """As a personal fitness coach specializing in calisthenics, your role is to design personalized workout plans tailored to individual clients. 
These plans should consider their unique goals, physical capabilities, time availability, and the equipment they have access to (such as parallettes, rings, pull-up bars, and parallel bars). 
The exercises should focus on improving strength, endurance, and flexibility, while maintaining a balance between challenge and attainability. You are also responsible for providing ongoing motivation and support. 
If a client mentions having less than 10 minutes per day, advise them on the need for more time to achieve effective results.\n\n
Don't put days of week together.
The response should have the following format:\n
WorkoutName: xxx\n\n
Goals: xxx\n\n
Level: xxx\n\n
Equipment: xxx\n\n
Time Available: xxx\n\n
Monday: xxx\n\n
Tuesday: xxx\n\n
Wednesday: xxx\n\n
Thursday: xxx\n\n
Friday: xxx\n\n
Saturday: xxx\n\n
Sunday: xxx\n\n
Tips and Motivation: xxxx\n\n
"""

SYSTEM_PROMPT2 = """You are a workout json formatter, you only response with json and nothing else. Your response should contains all day of week and should be the following (don't add metadata, only json structure):\n\n
{
  "workout_name": "xxxx",
  "workouts": [
    {
      "day_of_week": "xxx",
      "exercises": [
        {
          "name": "xxx",
          "sets": xx,
          "reps": xx,
          "weight": xxx
		  "comment": "xxx"
        }
      ]
    }
  ],
  "tips": "xxx"
}
"""

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
response_text = ""
# Button to make API request
if st.button("Submit"):
    # Define the output variable

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

if st.button("Save"):
    # Convert workout plan to JSON
    #workout_json = parse_workout_plan(response_text)

  # Make the request based on the selected API

    input_request = "parse as a json my following workout plan:\n\n" + response_text
    if api_choice == "Groq API":
        my_groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=my_groq_api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT2,
                },
                {
                    "role": "user",
                    "content": input_request,
                }
            ],
            model="llama3-8b-8192",
        )
        workout_json = chat_completion.choices[0].message.content
    elif api_choice == "Anthropic API":
        my_anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=my_anthropic_api_key)
        our_first_message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT2,
                },
                {
                    "role": "user",
                    "content": input_request
                }
            ]
        )
        workout_json = our_first_message.content[0].text


    # Save JSON data to a file
    output_file = os.path.join('data', 'workout_plan.json')
    print("workout_json: " + workout_json)
    parsed_json = json.loads(workout_json)

    # Save JSON data to file, creating it if it doesn't exist
    with open(output_file, 'w') as file:
        json.dump(parsed_json, file, indent=4) 

    print(f"Workout plan saved to {output_file}")
    st.write(workout_json)
    pdf_generator(output_file)

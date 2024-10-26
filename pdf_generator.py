import json
import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Workout Plan: ' + self.title, 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, exercises):
        # Set font for the table header
        self.set_font('Arial', 'B', 12)
        self.cell(60, 10, 'Exercise', 1)
        self.cell(30, 10, 'Sets', 1)
        self.cell(30, 10, 'Reps', 1)
        self.cell(30, 10, 'Weight', 1)
        self.ln()  # Move to the next line after header

        # Set font for the table body
        self.set_font('Arial', '', 12)
        
        # Initialize a list to hold comments
        comments = []
        
        for exercise in exercises:
            if exercise['name'] == "Rest Day":
                self.cell(0, 10, exercise['name'], 1)
                self.ln()
            else:
                # Fill table without comments
                self.cell(60, 10, exercise['name'], 1)
                self.cell(30, 10, str(exercise['sets']), 1)
                self.cell(30, 10, str(exercise['reps']), 1)
                self.cell(30, 10, str(exercise['weight']), 1)
                self.ln()
                
                # Add comment to the comments list
                comments.append(f"{exercise['name']}: {exercise['comment']}")
        
        # Add comments at the end of the day
        self.set_font('Arial', 'I', 12)  # Italics for comments
        self.cell(0, 10, 'Comments:', 0, 1, 'L')
        for comment in comments:
            self.multi_cell(0, 10, comment)
        self.ln(2)  # Add space after comments





def generate_workout_pdf(json_file, pdf_file_name):
    # Load the JSON data
    with open(json_file) as f:
        data = json.load(f)

    # Create a PDF document
    pdf = PDF()
    pdf.title = data['workout_name']  # Set the title for the header
    pdf.add_page()

    # Add workout sections
    for workout in data['workouts']:
        pdf.chapter_title(workout['day_of_week'])
        pdf.chapter_body(workout['exercises'])

    # Add tips at the end
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Tips:', 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, data['tips'])

    # Save the PDF
    pdf.output(pdf_file_name)

def main(json_file='workout_plan.json'):
    # Ensure the 'data' directory exists
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)

    pdf_file_name = os.path.join(output_dir, 'workout_plan.pdf')  # Define the output file path
    generate_workout_pdf(json_file, pdf_file_name)
    print(f"PDF generated: {pdf_file_name}")

if __name__ == "__main__":
    main()

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
        self.cell(75, 10, 'Exercise', 1)
        self.cell(20, 10, 'Sets', 1)
        self.cell(30, 10, 'Reps', 1)
        self.cell(55, 10, 'Tools', 1)
        self.ln()  # Move to the next line after header

        # Set font for the table body
        self.set_font('Arial', '', 10)
        
        comments = []
        
        for exercise in exercises:
            if exercise['name'] == "Rest Day":
                self.cell(0, 10, exercise['name'], 1)
                self.ln()
            else:
                # Calculate the row height based on the tallest cell (multi_cell for "Tools")
                exercise_height = self.get_string_width(exercise['name']) // 55 + 1
                sets_height = 1  # Fixed height for sets and reps columns
                reps_height = 1
                tools_height = self.get_string_width(exercise['tools']) // 55 + 1
                row_height = max(exercise_height, sets_height, reps_height, tools_height) * 10
                
                # Render cells with consistent row height
                self.cell(75, row_height, exercise['name'], 1)
                self.cell(20, row_height, str(exercise['sets']), 1)
                self.cell(30, row_height, str(exercise['reps']), 1)
                self.cell(55, row_height, str(exercise['tools']), 1)  # Use a fixed height for this
                
                # Move to the next line after filling the row
                self.ln(row_height)  # Move down only by the height of the row
                
                # Capture comments for separate section
                comments.append(f"{exercise['name']}: {exercise['comment']}")

        # Add comments at the end of the day
        self.set_font('Arial', 'I', 10)  # Italics for comments
        self.cell(0, 10, 'Comments:', 0, 1, 'L')
        max_width = self.w - self.l_margin - self.r_margin
        for comment in comments:
            self.cell(max_width, 10, comment)
            self.ln(10)
        #self.ln(len(5*comments))
        self.ln()




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
    pdf.set_font('Arial', '', 10)  # Reduce font size for tips

    # Define a maximum width considering page margins
    max_width = pdf.w - pdf.l_margin - pdf.r_margin

    for tip in data['tips']:
        pdf.cell(max_width, 10, tip)  # Use max_width for wrapping
        pdf.ln()

    # Save the PDF
    pdf.output(pdf_file_name)


def main(json_file='workout_plan.json'):
    # Ensure the 'data' directory exists
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)

    pdf_file_name = os.path.join(output_dir, 'workout_plan.pdf')  # Define the output file path
    generate_workout_pdf(json_file, pdf_file_name)
    print(f"PDF generated: {pdf_file_name}")

    return pdf_file_name

if __name__ == "__main__":
    main()

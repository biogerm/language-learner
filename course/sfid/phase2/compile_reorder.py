import json

# This is an estimated frequency order for SFI D National Exams writing topics (from highest frequency to lowest)
EXAM_FREQ_ORDER = [
    "Arbetsliv",            # Most common: job applications, work environment
    "Samhälle & Politik",   # Very common: opinion pieces (insändare), formal complaints
    "Vardagsliv",           # Very common: housing, daily issues, informal letters
    "Relationer & Känslor", # Common: informal letters giving advice or talking about feelings
    "Utbildning",           # Common: discussing studies, SFI, future plans
    "Hälsa & Medicin",      # Common: stress, diet, exercise
    "Natur & Miljö",        # Occasional: recycling, environment in opinion pieces
    "Kultur & Nöje",        # Occasional: reviews of books/movies, leisure time
    "Resor & Transport",    # Occasional: public transport complaints/suggestions
    "Mat & Matlagning",     # Less common as a main writing topic
    "Vetenskap & Teknik"    # Least common writing topic
]

def format_step_id(theme):
    return theme.lower().replace(' & ', '_').replace(' ', '_')

def reorder():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        course = json.load(f)
        
    steps_map = {step["step_title"]: step for step in course["steps"]}
    
    new_steps = []
    # Assign new step_ids based on this new order
    for i, theme in enumerate(EXAM_FREQ_ORDER):
        if theme in steps_map:
            step = steps_map[theme]
            step["step_id"] = f"step_{(i+1):02d}"
            new_steps.append(step)
            
    course["steps"] = new_steps
    
    with open("sfid_phase2_articles.json", "w", encoding="utf-8") as f:
        json.dump(course, f, ensure_ascii=False, indent=2)
        
    print("Successfully re-ordered steps based on SFI D Exam Frequency.")

if __name__ == "__main__":
    reorder()

import os
import pandas as pd
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from main import process_image_question, get_image_url

load_dotenv()

# Configure logging to see errors clearly
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load courses from Excel file
COURSES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'NPTEL-Sheet.xlsx')
courses_data = None

def load_courses():
    """Load courses from Excel file. Uses Course ID and Course Name only."""
    global courses_data
    try:
        df = pd.read_excel(COURSES_FILE)
        
        # Normalize column names (handle spaces, case variations)
        df.columns = df.columns.str.strip()
        
        # Look specifically for "Course ID" and "Course Name" columns
        id_col = None
        name_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            # Look for Course ID (not Code, not S No)
            if 'course id' in col_lower or (col_lower == 'id' and 'course' in str(df.columns).lower()):
                if id_col is None:
                    id_col = col
            # Look for Course Name
            if 'course name' in col_lower or (col_lower == 'name' and 'course' in str(df.columns).lower()):
                if name_col is None:
                    name_col = col
        
        # If not found, try to infer from common patterns
        if id_col is None:
            # Look for any column with "id" (but not "s no" or serial)
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'id' in col_lower and 's no' not in col_lower and 'serial' not in col_lower:
                    id_col = col
                    break
        
        if name_col is None:
            # Look for any column with "name" or "title"
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'name' in col_lower or 'title' in col_lower:
                    name_col = col
                    break
        
        # Fallback: use first two columns if still not found
        if id_col is None:
            id_col = df.columns[0] if len(df.columns) > 0 else 'Course ID'
        if name_col is None:
            name_col = df.columns[1] if len(df.columns) > 1 else 'Course Name'
        
        # Create standardized course list with Course ID and Course Name only
        courses_data = []
        for _, row in df.iterrows():
            course_id = str(row[id_col]).strip() if pd.notna(row[id_col]) else ''
            course_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ''
            
            # Replace hyphens with underscores in Course ID (e.g., noc26-ae07 -> noc26_ae07)
            course_id = course_id.replace('-', '_')
            
            # Skip if Course ID is empty or invalid
            if course_id and course_id.lower() not in ['nan', 'none', '']:
                courses_data.append({
                    'Course ID': course_id,
                    'Course Name': course_name or course_id
                })
        
        # Add cloud computing course if not already present
        cloud_computing_id = 'noc25_cs107'
        if not any(c.get('Course ID') == cloud_computing_id for c in courses_data):
            courses_data.append({
                'Course ID': cloud_computing_id,
                'Course Name': 'Cloud Computing'
            })
        
        return courses_data
    except Exception as e:
        logger.error(f"Error loading courses: {e}", exc_info=True)
        # Fallback to cloud computing only
        return [{
            'Course ID': 'noc25_cs107',
            'Course Name': 'Cloud Computing'
        }]

# Load courses on startup
try:
    courses_list = load_courses()
except:
    courses_list = [{'Course ID': 'noc25_cs107', 'Course Name': 'Cloud Computing'}]

@app.route('/')
def index():
    """Main page with course search and week input."""
    return render_template('index.html')

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """API endpoint to get all courses or search courses."""
    query = request.args.get('q', '').lower().strip()
    
    if query:
        # Filter courses based on search query (search by Course ID or Course Name)
        filtered = [
            course for course in courses_list
            if query in str(course.get('Course Name', '')).lower() or 
               query in str(course.get('Course ID', '')).lower()
        ]
        return jsonify(filtered)
    
    return jsonify(courses_list)

@app.route('/api/questions', methods=['POST'])
def get_all_questions_answers():
    """API endpoint to get all questions and answers for a given course and week."""
    data = request.json
    course_id = data.get('course_id')  # Use course_id, not course_code
    week = data.get('week')
    
    if not course_id or not week:
        return jsonify({'error': 'Course ID and week are required'}), 400
    
    try:
        week = int(week)
    except ValueError:
        return jsonify({'error': 'Week must be an integer'}), 400
    
    results = []
    
    # Process all 10 questions using Course ID
    for question_num in range(1, 11):
        image_url = get_image_url(course_id, week, question_num)
        
        try:
            # Process the question
            logger.debug(f"Processing question {question_num} for course {course_id}, week {week}")
            answers = process_image_question(image_url)
            results.append({
                'question_num': question_num,
                'success': True,
                'image_url': image_url,
                'answers': answers
            })
            logger.info(f"Successfully processed question {question_num}")
        except Exception as e:
            logger.error(f"Error processing question {question_num}: {str(e)}", exc_info=True)
            results.append({
                'question_num': question_num,
                'success': False,
                'error': str(e),
                'image_url': image_url,
                'answers': []
            })
    
    return jsonify({
        'success': True,
        'results': results
    })

if __name__ == '__main__':
    # Enable debug mode with better error visibility
    # When debug=True, Flask shows:
    # 1. Detailed error pages in browser
    # 2. Debugger PIN in terminal (use it to interact with errors)
    # 3. Auto-reload on code changes
    app.run(debug=True, port=5000, host='127.0.0.1')


from flask import Flask, render_template, request, jsonify
import json
from ai import generate_mcq_questions
from main import createForm

app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/about_project')
def about_project():
    return render_template('about_project.html')


@app.route('/home', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            topics = request.form['topics']
            num_questions = request.form['num_questions']
            doc_title = request.form['doc_title']
            form_title = request.form['form_title']
            form_description = request.form['form_description']
            question_level = request.form['question_level']
            marks = request.form['marks']
            
            # Convert num_questions and marks to integers
            num_questions = int(num_questions)
            marks = int(marks)
            
            # Create user data dictionary
            user_data = {
                'topics': topics,
                'num_questions': num_questions,
                'doc_title': doc_title,
                'form_title': form_title,
                'form_description': form_description,
                'question_level': question_level,
                'marks': marks
            }
            
            # Clean newlines from user data
            cleaned_user_data = {key: value.replace('\n', ' ') if isinstance(value, str) else value 
                                 for key, value in user_data.items()}
            
            # Dump the cleaned user data to JSON file
            with open('user_data.json', 'w') as f:
                json.dump(cleaned_user_data, f)
            
            # Generate MCQ questions
            generate_mcq_questions()
            
            # Load the generated questions from JSON file
            with open('generated_mcq_questions.json', 'r') as f:
                generated_questions = json.load(f)
            
            # Return the user data and generated questions as JSON
            return jsonify({'user_data': cleaned_user_data, 'generated_questions': generated_questions})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('index.html')


@app.route('/create_form', methods=['POST'])
def create_form():
    try:
        data = request.get_json()
        selected_questions_indices = data.get('selected_questions', [])
        
        with open('generated_mcq_questions.json', 'r') as f:
            all_questions = json.load(f)
        
        selected_questions = [all_questions[i] for i in selected_questions_indices]
        
        with open('selected_questions.json', 'w') as f:
            json.dump(selected_questions, f, indent=2)
        
        formId = createForm()
        form_link = f"https://docs.google.com/forms/d/{formId}"
        
        return jsonify({'form_link': form_link})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

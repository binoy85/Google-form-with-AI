import os
import re
import json
import google.generativeai as genai
from pydantic import BaseModel, ValidationError
from typing import List
import math 

# Define the Pydantic model for the MCQ structure
class MCQModel(BaseModel):
    question: str
    Option1: str
    Option2: str
    Option3: str
    Option4: str
    answer: str

# Convert the Pydantic model instance to a JSON string
def model_to_json(model_instance):
    return model_instance.model_dump_json()

# Extract JSON string from the text response
def extract_json(text_response):
    pattern = r'\{[^{}]*\}'
    matches = re.finditer(pattern, text_response)
    json_objects = []
    for match in matches:
        json_str = match.group(0)
        try:
            json_obj = json.loads(json_str)
            json_objects.append(json_obj)
        except json.JSONDecodeError:
            extended_json_str = extend_search(text_response, match.span())
            try:
                json_obj = json.loads(extended_json_str)
                json_objects.append(json_obj)
            except json.JSONDecodeError:
                continue
    return json_objects

# Extend search to capture nested JSON structures
def extend_search(text, span):
    start, end = span
    nest_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            nest_count += 1
        elif text[i] == '}':
            nest_count -= 1
            if nest_count == 0:
                return text[start:i+1]
    return text[start:end]

# Validate JSON with Pydantic model
def validate_json_with_model(model_class, json_data):
    validated_data = []
    validation_errors = []
    if isinstance(json_data, list):
        for item in json_data:
            try:
                model_instance = model_class(**item)
                validated_data.append(model_instance.dict())
            except ValidationError as e:
                validation_errors.append({"error": str(e), "data": item})
    elif isinstance(json_data, dict):
        try:
            model_instance = model_class(**json_data)
            validated_data.append(model_instance.dict())
        except ValidationError as e:
            validation_errors.append({"error": str(e), "data": json_data})
    else:
        raise ValueError("Invalid JSON data type. Expected dict or list.")
    return validated_data, validation_errors

def generate_mcq_questions():
    # Load user data
    with open('user_data.json', 'r') as f:
        data = json.load(f)

    # Base prompt for generating MCQ questions
    base_prompt = f"Generate {data['num_questions'] + math.ceil(data['num_questions'] /4)} MCQ questions for {data['question_level']}s on the topic of {data['topics']}. Each question should have four options and an answer in the following JSON format:"

    # Example JSON structure for the prompt
    example_json = model_to_json(MCQModel(
        question="Which of the following is NOT a state of a process?",
        Option1="Running",
        Option2="Waiting",
        Option3="Sleeping",
        Option4="Terminal",
        answer="Terminal"
    ))

    # Optimized prompt with the example JSON structure
    optimized_prompt = base_prompt + f" {example_json}"

    # Configure the GEMINI LLM
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')

    # Generate the response from the model
    response_text = model.generate_content(optimized_prompt).text

    # Extract JSON from the response
    json_objects = extract_json(response_text)

    # Validate the JSON structure
    validated, errors = validate_json_with_model(MCQModel, json_objects)

    # Save the validated questions to a JSON file
    with open("generated_mcq_questions.json", 'w') as f:
        json.dump(validated, f, indent=2)

    if errors:
        print("Validation errors occurred:", errors)

# Call the function to generate the questions


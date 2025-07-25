import os
import json
from groq import Groq
from collections import Counter
from typing import List
from dotenv import load_dotenv

load_dotenv()

def process_image_question(image_url: str, api_key: str = None) -> List[str]:
    """
    Process an image containing a question with multiple-choice options using Groq APIs.
    Use a multimodal model to extract text, then query text-to-text models to get the correct answer(s).
    Return the most common correct answer(s).
    
    Args:
        image_url (str): URL of the image containing the question and options
        api_key (str, optional): Groq API key. If None, uses GROQ_API_KEY environment variable
    
    Returns:
        List[str]: List of the most common correct answer(s)
    """
    # Initialize API key
    api_key = api_key or os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set and no API key provided")
    
    # Initialize Groq client
    client = Groq(api_key=api_key)
    
    # Model for text extraction (multimodal)
    text_extraction_model = "meta-llama/llama-4-maverick-17b-128e-instruct"
    
    # Models for answering the question (text-to-text)
    answer_models = [
        "qwen/qwen3-32b",
        "llama3-70b-8192",
        "deepseek-r1-distill-llama-70b",
        "gemma2-9b-it"
    ]
    
    # System prompt for text extraction
    text_extraction_prompt = """
    You are an expert at extracting text from images. Extract all text from the provided image, including the question and multiple-choice options, and return it as a single string.
    Ensure the output is clear and preserves the structure (e.g., question followed by options).
    """
    
    # System prompt for answering
    answer_prompt = """
    You are an expert at answering multiple-choice questions. Given the question and options, provide the correct answer(s) in JSON format.
    If multiple answers are correct, include all correct options in a list.
    Ensure the output is a valid JSON object with a 'correct_answers' key containing a list of option identifiers (e.g., ['A', 'B']).
    If no answer is correct or the question is unclear, return an empty list.
    """
    
    # Step 1: Extract text from image
    try:
        text_extraction_completion = client.chat.completions.create(
            model=text_extraction_model,
            messages=[
                {"role": "system", "content": text_extraction_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all text from the image."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            temperature=0.3,
            max_completion_tokens=2048
        )
        extracted_text = text_extraction_completion.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error extracting text with {text_extraction_model}: {str(e)}")
    
    # Step 2: Query text-to-text models with extracted text
    all_responses = []
    
    for model in answer_models:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": answer_prompt},
                    {
                        "role": "user",
                        "content": f"Question and options:\n{extracted_text}\n\nProvide the correct answer(s) in JSON format."
                    }
                ],
                temperature=0.5,
                max_completion_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            response = completion.choices[0].message.content
            response_json = json.loads(response)
            correct_answers = response_json.get("correct_answers", [])
            
            if isinstance(correct_answers, list):
                all_responses.append(correct_answers)
            else:
                print(f"Warning: Invalid response format from model {model}")
                
        except Exception as e:
            print(f"Error querying model {model}: {str(e)}")
            continue
    
    if not all_responses:
        raise RuntimeError("No valid responses received from any model")
    
    # Flatten all responses into a single list for counting
    flattened_answers = [answer for response in all_responses for answer in response]
    
    # Count occurrences of each answer
    answer_counts = Counter(flattened_answers)
    
    # Find the maximum count
    max_count = max(answer_counts.values()) if answer_counts else 0
    
    # Get all answers with the maximum count
    most_common_answers = [
        answer for answer, count in answer_counts.items() if count == max_count
    ]
    
    # Sort answers for consistent output
    most_common_answers.sort()
    
    return most_common_answers

week = int(input("Enter Week: "))


for i in range(1, 11):
    sample_image_url = f"https://storage.googleapis.com/swayam-node1-production.appspot.com/assets/img/noc25_cs107/w{week}q{i}.PNG"

    try:
        result = process_image_question(sample_image_url)
        print(f"Most common correct answer(s) for {i}:", result)
    except Exception as e:
        print(f"Error: {str(e)}")


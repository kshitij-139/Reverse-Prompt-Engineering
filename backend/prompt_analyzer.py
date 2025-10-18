# backend/prompt_analyzer.py

import os
import spacy
import joblib
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (for OPENAI_API_KEY)
load_dotenv()

# --- Load Models and Clients ---
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# 1. Load your trained ML Model
MODEL_PATH = Path(__file__).parent / "prompt_classifier.pkl"
try:
    PROMPT_MODEL = joblib.load(MODEL_PATH)
    print("Successfully loaded 'prompt_classifier.pkl'")
except FileNotFoundError:
    PROMPT_MODEL = None
    print(f"Warning: Model file not found at {MODEL_PATH}")

# 2. Load your OpenAI Client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# 3. Define the mapping from model labels to suggestions
SUGGESTION_MAP = {
    'is_vague': "Prompt might be too vague. Consider adding more specific details or context.",
    'no_action_verb': "Add a clear action verb to define the task (e.g., 'Summarize', 'Explain', 'List').",
    'no_format': "Specify the desired output format (e.g., 'in bullet points', 'as a JSON object')."
}

# --- Core Logic Functions ---

def extract_keywords(prompt: str) -> list:
    doc = nlp(prompt)
    return [token.text for token in doc if token.is_alpha and not token.is_stop][:5]

def get_readability_score(prompt: str) -> str:
    if len(prompt.split()) < 5:
        return "Difficult"
    if len(prompt.split()) > 20:
        return "Moderate"
    return "Easy"

def get_heuristic_suggestions(prompt: str) -> dict:
    """
    Analyzes the prompt using our trained ML model.
    """
    suggestions = []
    
    if PROMPT_MODEL:
        try:
            # Predict the problems
            pred_labels = PROMPT_MODEL.predict([prompt])[0]
            
            label_names = ['is_vague', 'no_action_verb', 'no_format']
            
            for i, label_name in enumerate(label_names):
            # ---------------------
                if pred_labels[i] == 1 and label_name in SUGGESTION_MAP:
                    suggestions.append(SUGGESTION_MAP[label_name])

        except Exception as e:
            suggestions.append(f"Model prediction error: {e}")
                
    else:
        suggestions.append("Warning: Prompt analysis model 'prompt_classifier.pkl' could not be loaded.")

    return {
        "keywords": extract_keywords(prompt),
        "readability": get_readability_score(prompt),
        "suggestions": suggestions if suggestions else ["Looks like a solid prompt!"]
    }

# --- THESE FUNCTIONS USE THE OPENAI API ---
def get_llm_improvement(prompt: str) -> str:
    """Uses OpenAI API to rewrite and improve the given prompt."""
    if not client:
        return "OpenAI API key not found. Please set it in your .env file."
        
    try:
        system_message = (
            "You are an expert prompt engineering assistant. Your task is to refine and "
            "improve the user's prompt to make it more effective, clear, and specific for a large language model. "
            "Return ONLY the improved prompt, without any preambles, explanations, or quotes."
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Improve this prompt: {prompt}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred with the OpenAI API: {e}"

def generate_llm_output(prompt: str) -> str:
    """Runs a given prompt against the OpenAI API and returns the output."""
    if not client:
        return "OpenAI API key not found. Please set it in your .env file."
        
    try:
        system_message = "You are a helpful assistant."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred with the OpenAI API: {e}"
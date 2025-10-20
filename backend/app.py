# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import prompt_analyzer
import logging # <-- Import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_prompt_endpoint():
    """API endpoint to analyze a prompt."""
    data = request.get_json()
    if not data or 'prompt' not in data:
        logging.error("Received request with no prompt data.") # <-- Log error
        return jsonify({"error": "No prompt provided"}), 400

    prompt = data['prompt']
    use_llm = data.get('use_llm', False)

    # --- ADD LOGGING ---
    logging.info(f"Received /analyze request. Prompt: '{prompt}', Use LLM: {use_llm}")
    # -------------------

    heuristics = prompt_analyzer.get_heuristic_suggestions(prompt)
    response_data = {"heuristics": heuristics}

    if use_llm:
        llm_suggestion = prompt_analyzer.get_llm_improvement(prompt)
        # --- ADD LOGGING ---
        logging.info(f"Generated LLM suggestion: '{llm_suggestion}'")
        # -------------------
        response_data["llm_suggestion"] = llm_suggestion

    return jsonify(response_data)

@app.route('/generate', methods=['POST'])
def generate_output_endpoint():
    """API endpoint to generate output from a given prompt."""
    data = request.get_json()
    if not data or 'prompt' not in data:
        logging.error("Received /generate request with no prompt data.") # <-- Log error
        return jsonify({"error": "No prompt provided for generation"}), 400

    prompt = data['prompt']
    logging.info(f"Received /generate request. Prompt: '{prompt}'") # <-- Log info

    llm_output = prompt_analyzer.generate_llm_output(prompt)
    logging.info(f"Generated LLM output: '{llm_output[:100]}...'") # <-- Log info (truncated)

    return jsonify({"output": llm_output})

if __name__ == '__main__':
    # When running locally, Flask's default logger is used.
    # The basicConfig above primarily affects production environments like Render.
    app.run(debug=True, port=5000)
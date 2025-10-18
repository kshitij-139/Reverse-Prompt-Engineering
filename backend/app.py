# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import prompt_analyzer 

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_prompt_endpoint():
    """API endpoint to analyze a prompt."""
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400

    prompt = data['prompt']
    use_llm = data.get('use_llm', False)

    # Call the function from prompt_analyzer.py
    heuristics = prompt_analyzer.get_heuristic_suggestions(prompt)
    
    response_data = {"heuristics": heuristics}

    if use_llm:
        # Call the function from prompt_analyzer.py
        llm_suggestion = prompt_analyzer.get_llm_improvement(prompt)
        response_data["llm_suggestion"] = llm_suggestion
        
    return jsonify(response_data)

@app.route('/generate', methods=['POST'])
def generate_output_endpoint():
    """API endpoint to generate output from a given prompt."""
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided for generation"}), 400
        
    prompt = data['prompt']
    
    # Call the function from prompt_analyzer.py
    llm_output = prompt_analyzer.generate_llm_output(prompt)
    
    return jsonify({"output": llm_output})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
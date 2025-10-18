# frontend/app.py

import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Inverse Prompt Engineering",
    layout="wide"
)

# --- API URLs ---
ANALYZE_URL = "http://127.0.0.1:5000/analyze"
GENERATE_URL = "http://127.0.0.1:5000/generate"

# --- Initialize Session State ---
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "improved_prompt" not in st.session_state:
    st.session_state.improved_prompt = ""
if "final_output" not in st.session_state:
    st.session_state.final_output = ""

# --- UI Components ---
st.title("NLP Reverse Prompt-Engineering Tool")
st.markdown("Analyze, improve, and test your LLM prompts in one place.")
st.divider()

# --- 3-Column Layout ---
col1, col2, col3 = st.columns(3, gap="medium")

# --- COLUMN 1: INPUT ---
with col1:
    st.header("1. Input Prompt")
    prompt_text = st.text_area(
        "Enter your prompt here...", 
        height=150, 
        placeholder="e.g., Explain quantum computing"
    )
    
    use_llm_checkbox = st.checkbox("Get AI-powered improvement")
    
    if st.button("Analyze Prompt", type="primary", use_container_width=True):
        # Reset state on every new analysis
        st.session_state.analysis_results = None
        st.session_state.improved_prompt = ""
        st.session_state.final_output = ""
        
        if not prompt_text.strip():
            st.warning("Please enter a prompt to analyze.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    payload = {"prompt": prompt_text, "use_llm": use_llm_checkbox}
                    response = requests.post(ANALYZE_URL, json=payload)
                    response.raise_for_status()
                    results = response.json()
                    
                    st.session_state.analysis_results = results
                    if use_llm_checkbox:
                        st.session_state.improved_prompt = results.get("llm_suggestion", "")

                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: Could not connect to the backend. Is it running?")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

# --- COLUMN 2: HEURISTIC ANALYSIS ---
with col2:
    st.header("2. Heuristic Analysis")
    
    # This column only shows content after analysis is run
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        heuristics = results.get("heuristics", {})
        
        st.write(f"**Readability:** `{heuristics.get('readability', 'N/A')}`")
        
        st.write("**Keywords:**")
        st.json(heuristics.get('keywords', []))
        
        st.write("**Suggestions:**")
        for suggestion in heuristics.get('suggestions', []):
            st.info(f" {suggestion}")
    
    else:
        st.info("Run an analysis from Column 1 to see heuristic feedback here.")

# --- COLUMN 3: AI IMPROVEMENT & OUTPUT ---
with col3:
    st.header("3. AI Output")
    
    # This column only shows content if an AI-improved prompt was generated
    if st.session_state.improved_prompt:
        st.subheader("AI-Improved Prompt")
        st.text_area(
            "Suggested Improvement", 
            value=st.session_state.improved_prompt, 
            height=150,
            key="improved_prompt_display",
            disabled=False # Can be tweaked as per user's preference
        )
        
        st.divider()

        if st.button("Run Improved Prompt", use_container_width=True):
            with st.spinner("Generating final output..."):
                try:
                    payload = {"prompt": st.session_state.improved_prompt}
                    response = requests.post(GENERATE_URL, json=payload)
                    response.raise_for_status()
                    generation_result = response.json()
                    st.session_state.final_output = generation_result.get("output", "No output received.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: Could not connect to the backend.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        
        # Display the final output if it exists
        if st.session_state.final_output:
            st.subheader(" Generated Response")
            st.markdown(st.session_state.final_output)
    
    elif st.session_state.analysis_results:
        st.info("Check the 'Get AI-powered improvement' box in Column 1 and re-analyze to run the prompt here.")
        
    else:
        st.info("Run an analysis with AI improvement enabled to get the final output here.")
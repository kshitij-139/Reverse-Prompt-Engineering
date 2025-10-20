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
ANALYZE_URL = "https://reverse-prompt-engineering.onrender.com/analyze"
GENERATE_URL = "https://reverse-prompt-engineering.onrender.com/generate"

# --- Initialize Session State ---
if "input_prompt" not in st.session_state:
    st.session_state.input_prompt = ""
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "improved_prompt" not in st.session_state:
    st.session_state.improved_prompt = ""
if "final_output" not in st.session_state:
    st.session_state.final_output = ""

# --- UI Components ---
st.title("Inverse Prompt Engineering Tool")
st.markdown("Analyze, improve, and test your LLM prompts in one place.")
st.divider()

# --- 3-Column Layout ---
col1, col2, col3 = st.columns(3, gap="medium")

# --- COLUMN 1: INPUT ---
with col1:
    st.header("1. Input Prompt")

    # Text area is now a "controlled component" tied to session state
    st.session_state.input_prompt = st.text_area(
        "Enter your prompt here...",
        value=st.session_state.input_prompt,
        height=150,
        placeholder="e.g., Explain quantum computing"
    )

    use_llm_checkbox = st.checkbox("Get AI-powered improvement")

    if st.button("Analyze Prompt", type="primary", use_container_width=True):
        st.session_state.analysis_results = None
        st.session_state.improved_prompt = "" 
        st.session_state.final_output = ""   


        if not st.session_state.input_prompt.strip():
            st.warning("Please enter a prompt to analyze.")
        else:
            with st.spinner("Analyzing... "):
                try:
                    payload = {
                        "prompt": st.session_state.input_prompt,
                        "use_llm": use_llm_checkbox
                    }
                    response = requests.post(ANALYZE_URL, json=payload, timeout=60)
                    response.raise_for_status() 
                    results = response.json()

                    st.session_state.analysis_results = results


                    if use_llm_checkbox and "llm_suggestion" in results:
                        st.session_state.improved_prompt = results.get("llm_suggestion", "")
                    else:
                        st.session_state.improved_prompt = ""

                # General connection errors
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: Could not connect to the backend API at {ANALYZE_URL}. Is it running correctly? Details: {e}")
                # Handle cases where backend sends invalid JSON
                except json.JSONDecodeError:
                    st.error("Error: Received an invalid response from the backend. Please check the backend logs.")
                # Catch-all for other unexpected errors
                except Exception as e:
                    st.error(f"An unexpected error occurred during analysis: {e}")

        
        st.rerun()
        
# --- COLUMN 2: HEURISTIC ANALYSIS ---
with col2:
    st.header("2. Heuristic Analysis")

    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        heuristics = results.get("heuristics", {}) 

        st.write(f"**Readability:** `{heuristics.get('readability', 'N/A')}`")

        st.write("**Keywords:**")
        st.json(heuristics.get('keywords', [])) 

        st.write("**Suggestions:**")
        suggestions = heuristics.get('suggestions', [])
        if suggestions:
            for suggestion in suggestions:
                
                if "⚠️" in suggestion or "Error" in suggestion or "Warning:" in suggestion:
                     st.error(f" {suggestion}") # Display backend errors clearly
                else:
                     st.info(f" {suggestion}") # Display normal suggestions
        else:
            is_model_load_warning = any("Warning: Prompt analysis model" in s for s in heuristics.get('suggestions', []))
            if is_model_load_warning:
                 st.error("⚙️ Warning: Prompt analysis model 'prompt_classifier.pkl' could not be loaded on the backend.")
            else:
                 st.info(" Looks like a solid prompt!") # Default positive message if no suggestions


    else:
        st.info("Run an analysis from Column 1 to see heuristic feedback here.")

# --- COLUMN 3: AI IMPROVEMENT & OUTPUT ---
with col3:
    st.header("3. AI Output")

    
    if st.session_state.improved_prompt:
        st.subheader(" AI-Improved Prompt")
        run_button_disabled = False 

        # Check for error messages returned from the backend's improvement function
        if "⚠️" in st.session_state.improved_prompt or "Error" in st.session_state.improved_prompt:
             st.error(st.session_state.improved_prompt)
             run_button_disabled = True 
        else:
            st.text_area(
                "Suggested Improvement",
                value=st.session_state.improved_prompt,
                height=150,
                key="improved_prompt_display", 
                disabled=False 
            )

        st.divider()

        
        if st.button("Run Improved Prompt", use_container_width=True, disabled=run_button_disabled):
            with st.spinner("Generating final output... (This might take a moment) "):
                try:
                    payload = {"prompt": st.session_state.improved_prompt}
                    response = requests.post(GENERATE_URL, json=payload, timeout=120)
                    response.raise_for_status()
                    generation_result = response.json()
                    st.session_state.final_output = generation_result.get("output", "Error: No output received from backend.")


                except requests.exceptions.Timeout:
                    st.error("Error: The generation request timed out. The AI model might be busy or the request is complex. Please try again. ")

                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: Could not connect to the backend API at {GENERATE_URL}. Details: {e}")

                except json.JSONDecodeError:
                    st.error("Error: Received an invalid response from the backend during generation.")

                except Exception as e:
                    st.error(f"An unexpected error occurred during generation: {e}")


        if st.session_state.final_output:
            st.subheader(" Generated Response")
            
            if "⚠️" in st.session_state.final_output or "Error" in st.session_state.final_output:
                st.error(st.session_state.final_output)
            else:
                
                st.markdown(st.session_state.final_output)

    
    elif st.session_state.analysis_results:
        st.info("Check the 'Get AI-powered improvement' box in Column 1 and re-analyze to enable running the prompt here.")
    else:
        st.info("Run an analysis (optionally with AI improvement enabled) to get the final output here.")
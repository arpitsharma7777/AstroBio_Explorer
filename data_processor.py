# In data_processor.py

# --- Replace the OpenAI client initialization ---
# from openai import OpenAI
import os
import re
import json
import google.generativeai as genai

# --- CONFIGURATION ---
# IMPORTANT: Set your Google AI Studio API Key via environment variable.
# Do NOT hard-code secrets in source code. Use a .env file (ignored by git) or
# set it in your shell: $env:GOOGLE_API_KEY = "your-key" on PowerShell
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
# --- (Keep the rest of your metadata and manual_entities the same) ---


def get_ai_summary(client, text_content):
    """
    Generates a 3-bullet summary for a given text using the Gemini API.
    """
    if not client or not GOOGLE_API_KEY:
        print("WARNING: Google API key not set. Skipping AI summary.")
        return {
            "objective": "AI summary requires a Google API key.",
            "key_result": "Please add your Google API key to data_processor.py.",
            "why_it_matters": "This feature requires a valid API key to function."
        }

    prompt = f"""
    Analyze the following scientific abstract and generate a summary in three distinct bullet points: Objective, Key Result, and Why it Matters.
    Provide the output ONLY in JSON format like this: {{"objective": "...", "key_result": "...", "why_it_matters": "..."}}

    Abstract:
    ---
    {text_content}
    ---
    """
    try:
        response = client.generate_content(prompt)
        raw_text = response.text.strip()
        # Try to extract JSON block using regex
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            summary_text = match.group(0)
        else:
            summary_text = raw_text.replace("```json", "").replace("```", "")
        try:
            summary = json.loads(summary_text)
        except Exception as e:
            print(f"Error parsing JSON from Gemini response: {e}\nRaw response: {raw_text}")
            # Fallback: return the raw text in all fields
            summary = {
                "objective": raw_text,
                "key_result": raw_text,
                "why_it_matters": raw_text
            }
        return summary
    except Exception as e:
        print(f"Error generating AI summary with Google AI: {e}")
        return {
            "objective": "Error during generation.",
            "key_result": "Could not process summary.",
            "why_it_matters": "There was an issue with the Google AI model call."
        }

def create_knowledge_graph():
    """
    Main function to build and save the knowledge graph.
    """
    print("Starting knowledge graph creation...")

    # Configure Google AI client
    genai.configure(api_key=GOOGLE_API_KEY)
    client = genai.GenerativeModel('gemini-1.5-flash')

    # (The rest of your create_knowledge_graph function remains exactly the same)
    #...
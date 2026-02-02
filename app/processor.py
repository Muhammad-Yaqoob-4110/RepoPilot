import os
from google import genai
from google.genai import types

class RepoProcessor:
    def __init__(self, model_name="gemini-3-flash-preview"):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = model_name
        self.code_map = None # Store it locally instead of on Google's cache server

    def set_context(self, code_map):
        """Simply stores the code map to be sent with queries."""
        self.code_map = code_map
        print("Context set. Gemini will use Implicit Caching for efficiency.")

    def get_query_response(self, user_query):
        if not self.code_map:
            return "Error: No code map found."

        system_instruction = (
            "You are a Senior Software Architect. You have the entire codebase in your context.\n\n"
            "FEATURE: IMPACT ANALYSIS\n"
            "When a user proposes a change (e.g., 'I want to change the response format'), you must:\n"
            "1. List all files that import or depend on the modified function.\n"
            "2. Rank the risk of the change (Low/Medium/High).\n"
            "3. Provide a 'Step-by-Step Implementation Plan' with specific file paths.\n\n"
            "FEATURE: ARCHITECTURE DIAGRAMS\n"
            "Always include a ```mermaid graph if a visual helps explain the data flow."
        )

        # We send the code_map as the FIRST part of the contents.
        # Gemini 3's implicit caching kicks in when the prefix (code_map) is repeated.
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                self.code_map, 
                f"\n\nUser Question: {user_query}"
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(include_thoughts=True)
            )
        )
        
        return response.text
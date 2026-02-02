import google.genai as genai
import os
from google.genai import types

def count_gemini_tokens(text, model_name="gemini-3-flash-preview"):
    """
    Count tokens using the correct google-genai API structure.
    """
    try:
        # Initialize client
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Create content in the correct format
        content = types.Content(
            parts=[types.Part(text=text)],
            role="user"
        )
        
        # Count tokens - note: count_tokens is on client.models
        response = client.models.count_tokens(
            model=model_name,
            contents=[content]
        )
        
        print(f"Token count successful: {response.total_tokens}")
        return response.total_tokens
        
    except Exception as e:
        print(f"Token count failed: {e}")
        # Estimate tokens
        estimated = len(text) // 4
        print(f"Using estimated tokens: {estimated}")
        return estimated
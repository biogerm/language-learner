import os
try:
    from google import genai
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='hello'
    )
    print(response.text)
except Exception as e:
    print(f"Error: {e}")

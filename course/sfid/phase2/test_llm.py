from google import genai
try:
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Translate "hej" to English.'
    )
    print(response.text)
except Exception as e:
    print(e)

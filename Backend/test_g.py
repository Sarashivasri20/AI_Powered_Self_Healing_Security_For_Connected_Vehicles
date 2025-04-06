from google import genai

def getResponse( contents, api_key = "", model = "gemini-2.0-flash"):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=contents,
    )
    return response.text
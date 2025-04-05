from google import genai

def getResponse( contents, api_key = "AIzaSyAc9e3_S0mtcx6twbf90BHU1ftbdF-T0xo", model = "gemini-2.0-flash"):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=contents,
    )
    return response.text
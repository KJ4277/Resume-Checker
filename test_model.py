from google import genai

client = genai.Client()  # reads GEMINI_API_KEY automatically

MODEL = "gemini-3.1-flash-lite-preview"

try:
    response = client.models.generate_content(
        model=MODEL,
        contents="Reply with exactly: the connection works",
    )
    print(response.text)
except Exception as e:
    print("ERROR:", e)
    print("\nModels available to your key:")
    for m in client.models.list():
        if "flash" in m.name:
            print(" ", m.name)
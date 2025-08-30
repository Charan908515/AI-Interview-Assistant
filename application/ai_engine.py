# ai_engine.py
import google.generativeai as genai

def configure_google_ai(api_key):
    """Configures the Google AI client with the provided key."""
    if not api_key:
        raise ValueError("Google AI API key was not provided.")
    genai.configure(api_key=api_key)

def build_chat(resume_summary):
    """Builds a chat instance. Assumes configure_google_ai has been called."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat(history=[
        {"role": "user", "parts": [f"You are a job interview assistant. Answer questions as a confident and professional candidate using the resume provided below. Keep your answers concise and to the point.\n\nRESUME:\n{resume_summary}"] }
    ])
    return chat

def get_response_from_chat_stream(chat, question):
    """Gets a streaming response from the chat. Yields text chunks (str)."""
    response_stream = chat.send_message(f"Interview question: {question}", stream=True)
    for chunk in response_stream:
        if chunk.text:
            yield chunk.text

def estimate_tokens(text: str) -> int:
    """
    Simple token approximation: count words.
    This is conservative and works as a rough token-to-credit mapping.
    """
    if not text: 
        return 0
    # you can refine this with a better tokenizer if you want
    return max(1, len(text.split()))

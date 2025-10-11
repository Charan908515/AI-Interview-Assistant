# ai_engine.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from typing import Generator

# Global LLM instance (configured once)
_llm = None

def configure_google_ai(api_key: str):
    """
    Configures the Google AI client with the provided key.
    Uses LangChain's ChatGoogleGenerativeAI instead of google.generativeai.
    """
    global _llm
    if not api_key:
        raise ValueError("Google AI API key was not provided.")

    _llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=api_key,
        temperature=0.7,
    )


def build_chat(resume_summary: str):
    """
    Builds a chat instance using the configured LLM.
    Returns a tuple (llm, history) to maintain context.
    """
    if _llm is None:
        raise RuntimeError("Google AI not configured. Call configure_google_ai(api_key) first.")

    system_prompt = (
        "You are a job interview assistant. "
        "Answer questions as a confident and professional candidate "
        "using the resume provided below. Keep your answers concise "
        "and to the point.\n\n"
        f"RESUME:\n{resume_summary}"
    )

    history = [SystemMessage(content=system_prompt)]
    print(">> testing the llm", _llm.invoke([HumanMessage(content="Hello")]))
    return (_llm, history)


def get_response_from_chat_stream(chat: tuple, question: str) -> Generator[str, None, None]:
    """
    Gets a streaming response from the chat.
    Yields text chunks (str) as they arrive.
    """
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

    llm, history = chat
    callbacks = [StreamingStdOutCallbackHandler()]
    print(">> Gemini called for:", question)

    history.append(HumanMessage(content=f"Interview question: {question}"))

    try:
        stream = llm.stream(history)
        for chunk in stream:
            if chunk.content:
                yield chunk.content
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print("[WARN] Streaming not available; falling back to invoke()")
            response = llm.invoke(history)
            yield response.content
        else:
            raise


def estimate_tokens(text: str) -> int:
    """
    Simple token approximation: count words.
    This is a rough token-to-credit mapping.
    """
    if not text:
        return 0
    return max(1, len(text.split()))

# resume_parser.py (LangChain version)
import PyPDF2
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

def get_resume_summary(file_path: str) -> str:
    """
    Reads a PDF and generates a summary using LangChain's Gemini model.
    This shares the same retry logic and avoids 429 errors.
    """
    try:
        # Initialize the model (safe to call repeatedly)
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,api_key=os.getenv("gemini_llm1")
        )

        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())

        if not text.strip():
            return "Could not summarize resume. The PDF appears to be empty or image-only."

        prompt = (
            "You are a professional resume summarizer. "
            "Summarize the key skills, experience, and projects clearly and concisely. "
            "Use about 5-7 sentences.\n\n"
            f"RESUME TEXT:\n{text}"
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        print(">> resume parser response:", response.content)
        return response.content
    except Exception as e:
        if "API key" in str(e):
            return "Could not summarize resume: Invalid or expired API key."
        return f"Could not summarize resume: {e}"

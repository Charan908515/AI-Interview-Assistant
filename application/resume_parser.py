# resume_parser.py (Updated)
import PyPDF2
import google.generativeai as genai

def get_resume_summary(file_path: str) -> str:
    """
    Reads a PDF and generates a summary.
    Assumes genai has been configured beforehand.
    """
    try:
        # Model is now initialized here to ensure genai is configured
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())

        if not text.strip():
            return "Could not summarize resume. The PDF appears to be empty or contains only images."

        prompt = f"You are a professional resume summarizer. Create a concise summary of the key skills, experience, and projects from the following resume text. This summary will be used by an AI to answer interview questions.\n\nRESUME TEXT:\n{text}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Provide a more specific error if the API key is likely the issue
        if "API key not valid" in str(e):
            return "Could not summarize resume. Your Google AI API key is invalid."
        return f"Could not summarize resume. An unexpected error occurred: {e}"

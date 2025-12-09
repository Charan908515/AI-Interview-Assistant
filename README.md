# AI Interview Assistant

AI Interview Assistant is a full-stack project that provides both:
- a web-based Credit Management / Interview Assistant (React frontend + FastAPI backend), and
- a standalone desktop assistant GUI (PyQt5) that uses real-time speech transcription, screen OCR, and a large language model (Google Gemini via a LangChain adapter) to answer interview-style questions based on a user-uploaded resume.

This README consolidates the repository-level overview and adds full details for the application (desktop) code which is the "main" executable component.


Table of contents
- Features / Specialities
- High-level architecture
- Notable files (web + application)
- Desktop application (the "exe") — what it does
- Environment variables (.env) & API keys
- Installing & running (desktop app)
- Web frontend & backend notes
- Packaging to a single executable
- Troubleshooting & tips
- Security recommendations
- Contributing

Features / Specialities
- Two complementary user experiences:
  - Web SPA (React) with authentication, credit model, payments and admin dashboard.
  - Desktop assistant (PyQt5) that:
    - Uploads/resumes PDFs and summarizes them with Gemini/LangChain.
    - Uses microphone streaming to transcribe speech (AssemblyAI streaming).
    - Shows a persistent floating overlay with current question + streaming AI answer.
    - Can capture the screen and run OCR to extract questions on-screen, then query the LLM.
    - Logs transcripts and AI responses to the backend and deducts credits automatically.
- Credit-based gating: desktop app checks and deducts credits via the backend before/after answering and logs activity.
- Streaming response support: LLM streaming is consumed and displayed chunk-by-chunk for responsive UX.
- Multi-component integration: LangChain (Google Gemini), AssemblyAI realtime, OCR.space (used), PyPDF2 for resume text extraction, sounddevice for microphone capture, websocket-client for realtime audio streaming.

High-level architecture
- frontend/ — React app (routes, auth context, API services). Connects to backend via the axios client in frontend/src/services/api.js.
- fastapi-backend/ — FastAPI backend (endpoints for auth, credits, payments, transcriptions, responses, admin).
- application/ — Desktop assistant implementation (PyQt5 UIs, audio capture, LLM glue code).
  - main_for_api.py — application entrypoint used to run the desktop assistant.
  - launcher_ui.py — login/launcher UI and dashboard for uploading resume, selecting microphone, starting the assistant.
  - overlay_ui2.py — floating overlay UI that displays streaming Q/A and controls (Get Answer, Capture Screen, Stop).
  - ai_engine.py — LLM glue (LangChain Google Gemini adapter, chat build, streaming/get_response helpers, token estimator).
  - resume_parser.py — resume PDF read & summarization helper (uses LangChain Gemini).
  - speech_api1.py — audio capture and AssemblyAI streaming websocket client + transcription callback handling.
  - missing_methods.py — helper snippets for UI styles (kept for reference).
  - requirements.txt — Python dependencies for the application.

Notable files and responsibilities
- frontend/src/services/api.js
  - Base URL configured to a deployed backend (changeable). Exposes grouped API helpers used by the React app.
- frontend/src/context/AuthContext.js
  - Centralized frontend auth state, token handling, refresh flow and helpers for updating credits in UI.
- application/main_for_api.py
  - The desktop app entrypoint. Shows the launcher window, loads saved token if present, starts the overlay & transcription threads, coordinates stop logic, and provides the main QApplication subclass.
- application/launcher_ui.py
  - Launcher window: login flow (calls backend /auth/login), resume upload (summarizer), microphone selection, start assistant button. Saves token to token.json and passes token into `MainApplication`.
- application/overlay_ui2.py
  - Floating overlay (always-on-top frameless) showing current transcribed question and streamed AI answer. Buttons to get answer, capture screen, and stop assistant are provided.
- application/ai_engine.py
  - Configures LangChain's ChatGoogleGenerativeAI (Gemini model) and exposes streaming & fallback logic. Also provides a simple token estimator (word-count based).
- application/resume_parser.py
  - Reads a PDF with PyPDF2, extracts text, and invokes Gemini (via LangChain) to produce a concise summary of the resume used as context for subsequent chat queries.
- application/speech_api1.py
  - Uses sounddevice to capture microphone input and streams audio to AssemblyAI's realtime websocket. Calls a supplied callback with partial/final transcripts and logs final transcripts to the backend.
- application/requirements.txt
  - Contains the Python packages needed to run the desktop assistant (PyQt5, langchain/google-genai or google-generativeai, PyPDF2, sounddevice, websocket-client, requests, mss, python-dotenv, keyboard).

Desktop application (the "exe") — what it does, end-to-end
1. Launch (python application/main_for_api.py)
   - App shows LauncherWindow (login UI).
   - User logs in with backend credentials (POST /auth/login). On success the access_token is saved to token.json and in the running QApplication instance.
2. Upload resume
   - User selects a PDF → resume_parser extracts text and calls Gemini to create a summary.
   - Summary stored in launcher instance and used as system context for the LLM.
3. Select microphone + Start Assistant
   - Devices enumerated by sounddevice; user selects an input.
   - On Start, app configures Gemini (ai_engine.configure_google_ai) and creates a chat instance (build_chat) seeded with the resume summary.
   - It then shows the floating overlay and starts the transcription thread (AssemblyAI) that streams microphone audio and calls back with transcribed text.
4. Ask questions / Capture screen
   - While speaking, transcriptions appear in the overlay. User can press "Get Answer" to fetch an answer from Gemini for the most recent transcript or "Capture Screen" to run OCR on a screenshot and query the LLM with on-screen content.
   - Streaming responses are displayed chunk-by-chunk on the overlay.
5. Credits and logging
   - Before/after server interactions, the app calls backend endpoints to check balance and deduct credits (e.g., POST /credits/deduct) and logs AI responses and transcriptions to /responses/ and /transcriptions/.
6. Stop
   - User can stop the assistant. Threads are signaled to stop gracefully, overlay closes and the launcher returns.

Environment variables (keys used by the application)
The application expects a .env file with API keys. Code references multiple environment variable names — please set the ones used in the code (or consolidate in your local copy and update code accordingly).

Common variables used across files:
- assembly_api_key
  - AssemblyAI realtime streaming API key (required for transcription websocket).
- ocr
  - API key for OCR.space (or another OCR provider) used by the screen capture -> OCR pipeline.
- gemini_llm1, gemini_llm2, gemini_llm5
  - These names appear across different modules:
    - resume_parser.py uses gemini_llm1
    - launcher_ui.py uses gemini_llm2
    - main_for_api.py reads gemini_llm5
  - All are used to configure or call Google Gemini via a LangChain adapter. To avoid errors set all or modify the code to use a single canonical variable name (e.g., GEMINI_API_KEY).
- Note: frontend src/services/api.js uses a separate endpoint base and stores tokens in browser localStorage; the desktop app uses token.json.

Suggested .env.example
GEMINI_API_KEY=your_gemini_api_key_here
assembly_api_key=your_assemblyai_realtime_key_here
ocr=your_ocr_space_api_key_here

If you keep the repo as-is, create the following keys (or duplicate GEMINI key across the three env names below to be safe):
gemini_llm1=...
gemini_llm2=...
gemini_llm5=...
assembly_api_key=...
ocr=...

Installing & running the desktop app (development)
1. Create virtual environment (recommended)
   - python -m venv .venv
   - source .venv/bin/activate   (macOS / Linux)
   - .venv\Scripts\activate      (Windows)
2. Install Python dependencies
   - pip install -r application/requirements.txt
3. Place API keys
   - Create a .env file in the repo root or the application directory containing the keys described above.
4. Run the application
   - python application/main_for_api.py
   - The launcher window should appear. Login via your backend (or the deployed backend if configured in API_BASE).
   - If you prefer to run overlay UI for testing only, application/overlay_ui2.py contains a small test harness (`if __name__ == '__main__'`) to exercise the UI without backend/LLM.

Backend/API integration notes (desktop)
- The desktop app uses the backend for:
  - POST /auth/login — authenticate user and obtain access_token (launcher_ui.py).
  - GET /credits/balance — read credit balance.
  - POST /credits/deduct — deduct credits after an answer.
  - POST /responses/ — log AI responses.
  - POST /transcriptions/ — log final transcriptions (speech_api1.py).
- Default backend base in the application code:
  - API_BASE = "https://se-project-backend-ddr9.onrender.com" in several modules.
  - speech_api1.py uses BACKEND_API_BASE = "http://127.0.0.1:8000" (note this difference).
- For a consistent local development setup, either run the FastAPI backend locally at the expected URL or edit the code to point to your backend location.

Packaging to a single executable (Windows .exe / macOS app)
- Common approach: PyInstaller (or similar bundlers).
- Example command (conceptual):
  - pip install pyinstaller
  - pyinstaller --onefile --add-data "path/to/your/resources;resources" application/main_for_api.py
- Packaging GUI apps requires careful handling of PyQt5, data files (icons, styles), the .env file and the included native libraries (sounddevice, PortAudio) — test thoroughly.
- When packaging, ensure the required native audio dependencies for sounddevice (PortAudio) are available on the target machine.

Troubleshooting & tips
- Missing API keys: The app performs checks and will show an error if Gemini/Assembly/OCR keys are missing. Confirm keys in .env and that os.getenv names match.
- Inconsistent env names: Several modules expect different gemini_* env names; either set all three or change the code to use a single environment variable.
- Microphone device selection: sounddevice can raise exceptions if device index is invalid. Use the "Select Microphone" UI and test devices listed by `sounddevice.query_devices()`.
- Platform-specific behavior:
  - overlay_ui2 tries to call a Windows-specific function (SetWindowDisplayAffinity) to exclude overlay from screen capture; this call is wrapped in a try/except and will fail gracefully on non-Windows systems.
- AssemblyAI websocket: network/firewall may block wss connections. Confirm connectivity and that your AssemblyAI subscription supports realtime streaming.
- OCR: application uses OCR.space API (ocr variable). OCR accuracy depends on the screenshot quality; image-only PDFs (resume) may not be summarized by resume_parser.
- 401 / invalid token: launcher_ui saves token.json locally. If the token becomes invalid, remove token.json, restart the launcher and log in again.
- Debug prints: launcher_ui.py and other modules contain debug prints to stdout which can help trace login and processing steps.

Security & privacy considerations
- Do not commit API keys in .env into source control.
- Transcripts and AI responses are logged to the backend when the app has a valid token — ensure your backend stores and secures these records appropriately.
- The overlay attempts to exclude itself from screenshots on Windows, but this is platform dependent.
- Use HTTPS for backend endpoints in production.

Suggestions for maintainers / improvements
- Consolidate Gemini environment variable names into a single canonical name (e.g., GEMINI_API_KEY) and update all modules.
- Externalize API_BASE into a config or environment variable for both frontend and desktop to ease local testing vs production.
- Add a .env.example at repo root showing required variables and expected formats.
- Add a small CLI or README section explaining how to package the desktop app (PyInstaller spec or brief Docker notes).
- Consider adding unit tests for resume_parser and ai_engine fallback logic.

Contributing
- Fork the repo, create a branch, run frontend/backend/application locally and submit a PR.
- Describe env variables and any local config changes in your PR description.

Contact / Maintainer
- Repository owner: GitHub user Charan908515

---
If you'd like, I can produce:
- A concise .env.example to put in the repository root,
- A short guide to unify env-key names and safe defaults,
- Or a sample PyInstaller spec for packaging the desktop app (one-off), but those changes involve editing files.

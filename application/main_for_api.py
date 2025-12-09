# main_for_api.py
import os, threading, requests, json
from PyQt5.QtWidgets import QApplication, QMessageBox
from dotenv import load_dotenv
import sys
# Import the enhanced UI components
from launcher_ui import LauncherWindow
from overlay_ui2 import FloatingOverlay, show_overlay  # keep as-is; file must exist
from ai_engine import get_response_from_chat_stream, estimate_tokens
from speech_api1 import start_transcription_thread, set_backend_token

# =========================
# Load ENV
# =========================
load_dotenv()
GEMINI_KEY = os.getenv("gemini_llm")

ASSEMBLY_KEY = os.getenv("assembly_api_key")
OCR_API_KEY = os.getenv("ocr")

# =========================
# Backend config
# =========================
DEPLOYED_API_BASE = "https://se-project-backend-ddr9.onrender.com"
API_BASE="http://localhost:8000"
TOKEN_FILE = "token.json"

stop_event = threading.Event()
chat = None
transcription_thread = None
overlay_window = None
latest_transcript = ""
END_UTTERANCE_TIMEOUT = 2.0

# =========================
# Backend helpers
# =========================
def save_token(token):
    with open(TOKEN_FILE, "w") as f: json.dump({"access_token": token}, f)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f).get("access_token")
    return None

def backend_get_credits(token):
    try:
        r = requests.get(f"{API_BASE}/credits/balance", headers={"Authorization": f"Bearer {token}"}, timeout=6)
        if r.status_code == 200:
            return r.json().get("credits", 0)
    except Exception as e:
        print("[CREDITS ERROR]", e)
    return 0

def backend_deduct_and_log(token, question, answer, tokens_used=None):
    if tokens_used is None:
        tokens_used = estimate_tokens(answer)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        requests.post(f"{API_BASE}/credits/deduct", headers=headers, json={"amount": tokens_used}, timeout=8)
        payload = {"query": question, "ai_response": answer, "tokens_used": tokens_used}
        requests.post(f"{API_BASE}/responses/", headers=headers, json=payload, timeout=8)
    except Exception as e:
        print("[CREDIT/LOG ERROR]", e)

# =========================
# OCR / AI pipeline
# =========================
def get_answer_from_screen():
    global overlay_window
    def do_capture():
        screenshot_path = "screenshot.png"
        try:
            # Capture the screen using PyQt5
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtGui import QPixmap
            
            app = QApplication.instance()
            screen = app.primaryScreen()
            if screen:
                # Capture the entire screen
                screenshot = screen.grabWindow(0)
                # Save the screenshot
                screenshot.save(screenshot_path, 'PNG')
                print(f"Screenshot captured and saved to {screenshot_path}")
            else:
                raise Exception("Could not access screen for capture")
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            if overlay_window:
                overlay_window.show()
            show_overlay('answer', f"Screenshot error: {e}")
            return
        finally:
            if overlay_window:
                overlay_window.show()
        threading.Thread(target=process_captured_image, args=(screenshot_path,), daemon=True).start()
    if overlay_window:
        overlay_window.hide()
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(250, do_capture)

def process_captured_image(image_path):
    global chat
    
    def reset_ui_state():
        # Reset the UI state
        show_overlay('question', "🎤 Listening...")
        if overlay_window:
            overlay_window.process_button.setEnabled(True)
            overlay_window.process_button.setCursor(overlay_window.PointingHandCursor)
            overlay_window.capture_button.setEnabled(True)
            overlay_window.capture_button.setText("📸 Capture Screen")
    
    try:
        # Validate input
        if not image_path or not os.path.exists(image_path):
            show_overlay('answer', "❌ Error: Screenshot file not found. Please try capturing the screen again.")
            reset_ui_state()
            return
            
        if not OCR_API_KEY or not OCR_API_KEY.strip():
            show_overlay('answer', "❌ Error: OCR API key is not configured\nPlease check your .env file and restart the application")
            reset_ui_state()
            return
        
        # Verify the image file is valid
        try:
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                raise ValueError("Screenshot file is empty (0 bytes)")
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise ValueError("Screenshot file is too large (max 10MB)")
        except OSError as e:
            raise Exception(f"Error accessing screenshot file: {str(e)}")
        
        show_overlay('question', "🔍 Processing screenshot...")
        show_overlay('answer', "Processing image, please wait...")
        
        # Prepare the OCR request with additional parameters for better accuracy
        payload = {
            'apikey': OCR_API_KEY.strip(),
            'language': 'eng',
            'isOverlayRequired': False,
            'OCREngine': 2,  # More accurate engine
            'detectOrientation': True,
            'scale': True,
            'isTable': False,
            'isCreateSearchablePdf': False,
            'isSearchablePdfHideTextLayer': True
        }
        
        # Send the request to OCR.space with better error handling
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/png')}
                response = requests.post(
                    "https://api.ocr.space/parse/image",
                    files=files,
                    data=payload,
                    timeout=45  # Increased timeout for better reliability
                )
        except requests.exceptions.Timeout:
            raise Exception("OCR service timed out. The server took too long to respond.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to OCR service: {str(e)}")
        
        # Check for HTTP errors with more detailed messages
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("Invalid OCR API key. Please check your .env file and restart the application.")
            elif response.status_code == 429:
                raise Exception("API rate limit exceeded. Please wait a few minutes and try again.")
            elif 500 <= response.status_code < 600:
                raise Exception("OCR service is currently unavailable. Please try again later.")
            else:
                raise Exception(f"OCR API error: {response.status_code} - {response.text}")
        
        # Parse the response with better error handling
        try:
            result = response.json()
        except json.JSONDecodeError:
            raise Exception("Invalid response from OCR service. The service might be experiencing issues.")
        
        # Check for API-specific errors
        if result.get('IsErroredOnProcessing', False):
            error_message = result.get('ErrorMessage', 'Unknown OCR error')
            if 'Invalid API key' in error_message:
                raise Exception("Invalid OCR API key. Please check your .env file and restart the application.")
            elif 'limit' in error_message.lower():
                raise Exception("API rate limit reached. Please wait before trying again.")
            else:
                raise Exception(f"OCR processing error: {error_message}")
        
        # Validate the response structure
        parsed = result.get('ParsedResults')
        if not parsed or not isinstance(parsed, list) or len(parsed) == 0:
            raise ValueError("No text could be extracted from the image. Please try a different area or adjust the image quality.")
            
        extracted = parsed[0].get('ParsedText', '').strip()
        if not extracted:
            raise ValueError("No readable text was found in the screenshot. Please ensure the text is clear and try again.")
        
        # Clean up the extracted text while preserving meaningful line breaks
        extracted = '\n'.join(line.strip() for line in extracted.split('\n') if line.strip())
        
        # Limit the length of the extracted text to prevent UI issues
        if len(extracted) > 2000:
            extracted = extracted[:2000] + "... [text truncated]"
        
        # Show the extracted text and get AI response
        show_overlay('question', extracted)
        question = f"Screen Question: {extracted}"
        
        # Get AI response with error handling
        try:
            full_resp = ""
            response_stream = get_response_from_chat_stream(chat, question) if chat else ["AI service not available"]
            for chunk in response_stream:
                full_resp += chunk
                show_overlay('answer', f"Q: {extracted}\n\nA: {full_resp}")
            
            # Log the interaction if user is authenticated
            token = getattr(QApplication.instance(), '_backend_token', None)
            if token:
                try:
                    backend_deduct_and_log(token, question, full_resp)
                except Exception as e:
                    print(f"[LOGGING ERROR] {e}")
        except Exception as e:
            show_overlay('answer', f"❌ Error getting AI response: {str(e)}\nThe text was extracted successfully: \n\n{extracted}")
            return
                
    except requests.exceptions.RequestException as e:
        show_overlay('answer', f"❌ Network error: {str(e)}\nPlease check your internet connection and try again.")
    except json.JSONDecodeError as e:
        show_overlay('answer', "❌ Error: Invalid response from OCR service. The service might be down or the response format changed.")
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg:
            show_overlay('answer', f"❌ {error_msg}")
        else:
            show_overlay('answer', f"❌ Error: {error_msg}\n\nIf this problem persists, please try the following:\n1. Ensure the text in the image is clear and well-lit\n2. Try capturing a different area\n3. Check your internet connection\n4. Restart the application")
    finally:
        # Clean up the screenshot file
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")
        
        # Reset the UI state
        reset_ui_state()

def get_ai_answer():
    global latest_transcript, chat
    if not latest_transcript:
        show_overlay('answer', "No question detected.")
        return
    q = latest_transcript.strip()
    show_overlay('answer', f"Q: {q}\n\nA: ...")
    full_resp = ""
    token = QApplication.instance()._backend_token
    if token and backend_get_credits(token) <= 0:
        show_overlay('answer', "Not enough credits.")
        return
    try:
        for chunk in get_response_from_chat_stream(chat, q):
            full_resp += chunk
            show_overlay('answer', f"Q: {q}\n\nA: {full_resp}")
        if token:
            backend_deduct_and_log(token, q, full_resp)
    except Exception as e:
        show_overlay('answer', f"AI error: {e}")
    finally:
        show_overlay('question', "Listening...")
        latest_transcript = ""

def get_ai_answer_threaded():
    """Wrapper to run get_ai_answer in a separate thread to avoid blocking the UI"""
    thread = threading.Thread(target=get_ai_answer, daemon=True)
    thread.start()


def handle_transcription(text, is_final):
    global latest_transcript
    # set latest_transcript (streaming or final)
    latest_transcript = text
    show_overlay('question', latest_transcript)

# =========================
# Application class
# =========================
class MainApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self._backend_token = None
        
        # Set application icon for all windows
        icon_path = os.path.join(os.path.dirname(__file__), "logo.ico")
        if os.path.exists(icon_path):
            from PyQt5.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))

        # Show login/launcher
        self.login_window = None
        token = load_token()
        if token:
            try:
                print("[AUTO LOGIN] Using saved token")
                self._backend_token = token
                self.launcher_window = LauncherWindow()
                self.launcher_window.show()
                return
            except Exception:
                pass

        self.login_window = LauncherWindow()
        self.login_window.show()

    def start_main_app(self, chat_instance, device_index, assembly_key, ocr_key):
        """Start the main interview assistant with overlay and transcription."""
        global chat, transcription_thread, overlay_window, stop_event
        chat = chat_instance
        set_backend_token(self._backend_token)

        # Create and show floating overlay
        overlay_window = FloatingOverlay(
            process_callback=get_ai_answer_threaded,
            capture_callback=get_answer_from_screen,
            stop_callback=stop_assistant
        )
        overlay_window.show()

        # reset stop_event
        stop_event = threading.Event()
        # Start transcription thread: note parameter order (api_key, callback, stop_event, device_index)
        transcription_thread = start_transcription_thread(assembly_key, handle_transcription, stop_event, device_index)

        # Hide launcher window if present
        if hasattr(self, 'launcher_window') and self.launcher_window:
            try:
                self.launcher_window.hide()
            except Exception:
                pass

def stop_assistant():
    """Stop the assistant and return to launcher"""
    global stop_event, overlay_window, transcription_thread
    
    print("Stopping assistant...")
    
    # Set stop event to signal all threads to stop
    if stop_event:
        stop_event.set()
    
    # Wait for transcription thread to finish
    if transcription_thread and transcription_thread.is_alive():
        print("Waiting for transcription thread to stop....")
        transcription_thread.join(timeout=3.0)  # Wait up to 3 seconds
        if transcription_thread.is_alive():
            print("Warning: Transcription thread did not stop gracefully")
    
    # Close overlay window
    if overlay_window:
        try:
            overlay_window.close()
        except Exception as e:
            print(f"Error closing overlay: {e}")
    
    # Reset global variables
    overlay_window = None
    transcription_thread = None
    
    # Show launcher window again
    app = QApplication.instance()
    if hasattr(app, 'launcher_window') and app.launcher_window:
        app.launcher_window.show()
        print("Returned to launcher window")
    else:
        print("No launcher window found, exiting application")
        app.quit()

def listen_for_escape_key():
    try:
        import keyboard
        keyboard.wait("esc")
        if QApplication.instance():
            QApplication.instance().quit()
    except Exception:
        pass




if __name__=="__main__":
    # Start escape key listener
    esc_thread = threading.Thread(target=listen_for_escape_key, daemon=True)
    esc_thread.start()
    
    # Create and show the application
    app = MainApplication(sys.argv)
    
    
    launch_thread = threading.Thread(
        target=LauncherWindow.launch_n,
        daemon=True
    )
    launch_thread.start()
    
    sys.exit(app.exec_())

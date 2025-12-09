# AI Interview Assistant - Project Documentation

## 📌 Project Overview
AI Interview Assistant is a sophisticated interview preparation platform that leverages artificial intelligence to help users practice and improve their interview skills. The application provides a realistic interview simulation environment with features like real-time transcription, AI-powered responses, and screen capture for question analysis.

## 🏗️ System Architecture

The application follows a client-server architecture with the following components:

### 1. Frontend (React.js)
- Modern, responsive user interface
- Interactive interview sessions
- Real-time feedback and assessment
- User authentication and session management
- Credit-based system for premium features

### 2. Backend (FastAPI)
- RESTful API endpoints
- User authentication (JWT)
- Credit management system
- Integration with AI services
- Database operations (PostgreSQL)

### 3. Desktop Application (Python/PyQt5)
- Launcher/Login interface
- Floating overlay for interview assistance
- Screen capture and OCR capabilities
- Integration with speech-to-text services
- Local token storage for authentication

## 🔑 Key Features

### AI-Powered Interview Simulation
- Realistic interview scenarios
- Context-aware responses
- Support for technical and behavioral questions

### Speech Recognition & Processing
- Real-time speech-to-text transcription
- Support for multiple languages
- End-of-utterance detection

### Screen Capture & OCR
- Capture interview questions from screen
- Optical Character Recognition (OCR) for text extraction
- Integration with AI for answer generation

### User Management
- Secure authentication
- Credit-based system
- Session management
- Progress tracking

## 🛠️ Technical Components

### Core Dependencies
- **Frontend**: React.js, Context API, Axios
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Desktop App**: PyQt5, AssemblyAI, Google Gemini AI
- **AI/ML**: Natural Language Processing, Speech Recognition

### External Services
- **AssemblyAI**: For speech-to-text transcription
- **Google Gemini AI**: For generating interview responses
- **OCR.space**: For optical character recognition

## 📂 Project Structure

```
.
├── application/              # Desktop application source
│   ├── ai_engine.py         # AI response generation
│   ├── launcher_ui.py       # Launcher/login window
│   ├── overlay_ui2.py       # Floating interview assistant
│   ├── resume_parser.py     # Resume parsing functionality
│   ├── speech_api1.py       # Speech-to-text integration
│   └── requirements.txt     # Python dependencies
│
├── fastapi-backend/         # Backend API server
│   ├── app/
│   │   └── main.py         # API endpoints
│   └── requirements.txt     # Backend dependencies
│
└── frontend/                # React frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── context/        # State management
    │   └── App.js          # Main application component
    └── package.json        # Frontend dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL
- API keys for AssemblyAI, Gemini AI, and OCR.space

### Installation
1. Clone the repository
2. Set up Python virtual environment and install dependencies:
   ```bash
   cd application
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```
4. Configure environment variables (create a `.env` file in the respective directories)

## 🤖 AI Integration

The application uses multiple AI services:

1. **Google Gemini AI**: For generating context-aware interview responses
2. **AssemblyAI**: For real-time speech recognition and transcription
3. **Custom AI Models**: For resume parsing and question analysis

## 🔒 Security Considerations

- JWT-based authentication
- Secure storage of API keys using environment variables
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure handling of user data

## 📈 Future Enhancements

1. **Advanced Analytics Dashboard**
   - Detailed performance metrics
   - Skill gap analysis
   - Personalized feedback reports

2. **Enhanced AI Capabilities**
   - Multi-modal input processing
   - Emotion and sentiment analysis
   - Personalized learning paths

3. **Collaboration Features**
   - Peer review system
   - Mock interview scheduling
   - Integration with calendar apps


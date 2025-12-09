# FastAPI Backend 

## Overview
This project is a FastAPI backend application designed to provide a robust and scalable API for the AI Interview Assistant platform. It implements user management, credit systems, payment processing, AI response handling, and speech transcription services. The application follows a modular structure, separating concerns into different directories for better organization and maintainability.

### Key Features
- User authentication and authorization
- Credit system management
- Payment processing integration
- AI response generation and handling
- Speech transcription services
- Admin panel functionality
- Secure database operations

## Backend Files Structure
```
fastapi-backend
├── Dockerfile                  # Docker configuration for containerization
├── README.md                  # Project documentation
├── requirements.txt           # Project dependencies
├── app
│   ├── main.py               # Entry point of the FastAPI application
│   ├── core
│   │   ├── auth.py          # Authentication and authorization
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   └── security.py      # Security utilities
│   ├── crud
│   │   ├── credit_crud.py   # Credit system operations
│   │   ├── payment_crud.py  # Payment processing operations
│   │   ├── response_crud.py # AI response handling
│   │   ├── transcription_crud.py # Speech transcription operations
│   │   └── user_crud.py     # User management operations
│   ├── database
│   │   ├── __init__.py      # Database package initialization
│   │   └── connection.py    # Database connection handling
│   ├── models
│   │   ├── __init__.py      # Models package initialization
│   │   ├── credit.py        # Credit system models
│   │   ├── payment.py       # Payment models
│   │   ├── response_log.py  # Response logging models
│   │   ├── transcription_log.py # Transcription logging models
│   │   └── user.py          # User models
│   ├── routes
│   │   ├── admins.py        # Admin panel routes
│   │   ├── ai_responses.py  # AI interaction routes
│   │   ├── auth.py          # Authentication routes
│   │   ├── credits.py       # Credit system routes
│   │   ├── payments.py      # Payment processing routes
│   │   └── transcription.py # Speech transcription routes
│   ├── schemas             # Pydantic schemas for data validation
│   └── utils              # Utility functions and helpers
└── tests
    └── test_main.py       # Unit tests for the application
```

## Setup Instructions
1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd fastapi-backend
   ```

2. **Create a virtual environment**:
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   Create a `.env` file in the root directory and add the necessary environment variables:
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   SECRET_KEY=your_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## Usage

### Running Locally
To run the FastAPI application locally, execute:
```
uvicorn app.main:app --reload
```

### Docker Deployment
To run the application using Docker:
```
docker build -t ai-interview-backend .
docker run -p 8000:8000 -d ai-interview-backend
```

### API Documentation
- Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`
- Alternative API docs (ReDoc): `http://127.0.0.1:8000/redoc`

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### User Management
- `GET /users/me` - Get current user info
- `PUT /users/me` - Update user profile

### Credits
- `GET /credits/balance` - Get user's credit balance
- `POST /credits/purchase` - Purchase credits

### AI Interactions
- `POST /ai/response` - Get AI interview responses
- `POST /transcription` - Speech-to-text conversion

### Payments
- `POST /payments/create` - Create payment session
- `GET /payments/history` - Get payment history


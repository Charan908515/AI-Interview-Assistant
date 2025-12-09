# Whisper AI- User and Credit Management System - Frontend

A React-based frontend application for the Credit Management System, providing user authentication, credit management, payment processing, and administrative functionality.

## Features

### User Features
- **Authentication**: User registration and login
- **Credit Management**: View credit balance, purchase credits
- **Payment Processing**: Make payments and view payment history
- **Activity Logging**: Log transcriptions and AI responses
- **Dashboard**: Overview of account status and activities

### Admin Features
- **User Management**: View, delete users, grant/deduct credits
- **Payment Management**: Monitor all payments and revenue
- **Dashboard Analytics**: System statistics and user insights
- **Advanced Filtering**: Search and sort users and payments

## Technology Stack

- **Frontend Framework**: React 18
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Styling**: CSS3 with custom components
- **State Management**: React Context API

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager

## Configuration

### API Base URL
The API base URL is configured in `src/services/api.js`:
```javascript
const API_BASE_URL = 'backend url';
```

### Proxy Configuration
The `package.json` includes a proxy configuration to forward API requests:
```json
"proxy": "backend url"
``` 

Replace the url with your backend url

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3000`

## Project Structure

```
frontend/
├── public/
│   └── index.html              # Main HTML template
├── src/
│   ├── components/
│   │   ├── auth/               # Authentication components
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   └── ProtectedRoute.js
│   │   ├── dashboard/          # User dashboard components
│   │   │   ├── Dashboard.js
│   │   │   ├── CreditManager.js
│   │   │   ├── PaymentHistory.js
│   │   │   └── ActivityLog.js
│   │   ├── admin/              # Admin panel components
│   │   │   ├── AdminDashboard.js
│   │   │   ├── AdminStats.js
│   │   │   ├── UserManagement.js
│   │   │   └── PaymentManagement.js
│   │   └── layout/             # Layout components
│   │       ├── Navbar.js
│   │       └── Navbar.css
│   ├── context/
│   │   └── AuthContext.js      # Authentication context
│   ├── services/
│   │   └── api.js              # API service layer
│   ├── App.js                  # Main application component
│   ├── App.css                 # Global styles
│   └── index.js                # Application entry point
├── package.json                # Dependencies and scripts
└── README.md                   # This file
```

## API Integration

The frontend integrates with the FastAPI backend through the following endpoints:

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Credits
- `POST /credits/add` - Add credits to user account
- `POST /credits/deduct` - Deduct credits from user account
- `GET /credits/balance` - Get current credit balance

### Payments
- `POST /payments/create` - Process a payment
- `GET /payments/history` - Get user payment history

### Transcriptions & AI Responses
- `POST /transcriptions/` - Log transcription
- `POST /responses/` - Log AI response

### Admin (Admin users only)
- `GET /admin/dashboard` - Get dashboard statistics
- `GET /admin/users` - Get all users
- `DELETE /admin/users/{user_id}` - Delete a user
- `POST /admin/users/{user_id}/grant_credits` - Grant credits to user
- `POST /admin/users/{user_id}/deduct_credits` - Deduct credits from user
- `GET /admin/payments` - Get all payments


```

## Authentication Flow

1. Users register or login through the auth forms
2. On successful authentication, a JWT token is stored in localStorage
3. The token is automatically included in all API requests via Axios interceptors
4. Protected routes redirect unauthenticated users to the login page
5. Admin routes require both authentication and admin privileges

## Component Overview

### Authentication Components
- **Login.js**: User login form with error handling
- **Register.js**: User registration form with validation
- **ProtectedRoute.js**: Route wrapper for authenticated access

### Dashboard Components
- **Dashboard.js**: Main user dashboard with stats and activities
- **CreditManager.js**: Credit purchase and activity logging
- **PaymentHistory.js**: User's payment transaction history
- **ActivityLog.js**: Recent account activities display

### Admin Components
- **AdminDashboard.js**: Main admin interface with tabbed navigation
- **AdminStats.js**: System statistics and recent activity overview
- **UserManagement.js**: User CRUD operations and credit management
- **PaymentManagement.js**: Payment monitoring and analytics

### Layout Components
- **Navbar.js**: Navigation bar with authentication status
- **Navbar.css**: Responsive navigation styling

## Styling

The application uses a custom CSS framework with:
- Responsive grid system
- Consistent color scheme
- Reusable component classes
- Mobile-first design approach
- Professional UI components

Key CSS classes:
- `.btn, .btn-primary, .btn-secondary` - Button styles
- `.card` - Card container styling
- `.form-group` - Form field wrapper
- `.alert, .alert-error, .alert-success` - Alert messages
- `.grid, .grid-2, .grid-3, .grid-4` - Responsive grid layouts

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run test suite
- `npm eject` - Eject from Create React App

### Environment Variables

Create a `.env` file in the frontend directory for environment-specific configurations:
```env
REACT_APP_API_URL=http://localhost:8000
```

## Production Build

1. Build the application:
   ```bash
   npm run build
   ```

2. The build files will be created in the `build/` directory

3. Deploy the build files to your web server

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Credit Management System and follows the same licensing terms.
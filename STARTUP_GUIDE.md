# Integrated Startup Guide

This guide explains how to start your full-stack application that combines the FastAPI backend with the React frontend.

## Quick Start

You have multiple options to start the integrated application:

### Option 1: Shell Script (Recommended)
```bash
./start.sh
```

### Option 2: Python Script
```bash
python start_integrated.py
```

### Option 3: Direct Command
```bash
uvicorn complete_app:app --host 0.0.0.0 --port 8000 --reload
```

## What Gets Started

When you run any of these startup methods, you get:

- **Backend API** running on `http://localhost:8000/api/`
- **Frontend React App** served at `http://localhost:8000/`
- **API Documentation** available at `http://localhost:8000/docs`
- **Interactive API Testing** at `http://localhost:8000/redoc`

## How It Works

Your application is already integrated! Here's how:

1. **`complete_app.py`** is your main FastAPI application
2. It serves the React frontend from the `frontend/build/` directory
3. API endpoints are prefixed with `/api/`
4. All other routes serve the React frontend (SPA routing)

## Application Structure

```
/data/qyu/projects/backend/
├── complete_app.py          # Main FastAPI app (serves both API and frontend)
├── start_integrated.py      # Python startup script
├── start.sh                 # Shell startup script
├── start_new_app.py        # Alternative backend-only startup
├── frontend/
│   ├── build/              # Built React app (served by FastAPI)
│   ├── src/                # React source code
│   ├── public/             # React public assets
│   └── package.json        # Frontend dependencies
├── app/                    # Backend application code
├── test/                   # Test suite
└── requirements.txt        # Backend dependencies
```

## Available Services

Once started, you can access:

### Frontend (React)
- **URL**: `http://localhost:8000/`
- **Features**: 
  - Student matching interface
  - Chat system with AI consultation
  - User authentication
  - Profile management

### Backend API
- **Base URL**: `http://localhost:8000/api/`
- **Key Endpoints**:
  - `POST /api/auth/login` - User authentication
  - `GET /api/students/` - List students
  - `POST /api/matching/match` - Find student matches
  - `GET /api/chat/history/{chat_id}` - Chat history
  - `POST /api/consultation/start` - Start AI consultation

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Development Mode

The startup scripts run with `--reload` flag, which means:
- ✅ Backend code changes reload automatically
- ❌ Frontend changes require rebuilding

To rebuild frontend after changes:
```bash
cd frontend
npm run build
```

## Troubleshooting

### Frontend Not Loading
```bash
cd frontend
npm install
npm run build
```

### Backend Errors
Check the terminal output for error messages. Common issues:
- Database connection problems
- Missing environment variables
- Port already in use

### Port Already in Use
If port 8000 is busy, you can use a different port:
```bash
uvicorn complete_app:app --host 0.0.0.0 --port 8080 --reload
```

## Testing

To run the comprehensive test suite:
```bash
python -m pytest test/ -v
```

All tests should pass with 100% success rate.

## Environment Setup

Make sure you have:
- Python 3.8+ with required packages (`pip install -r requirements.txt`)
- Node.js with npm (for frontend building)
- Supabase database configured
- Environment variables set up

## Production Deployment

For production, consider:
- Using a production WSGI server like Gunicorn
- Setting up a reverse proxy (nginx)
- Configuring environment-specific settings
- Building frontend with production optimizations

---

**Happy coding! 🚀**

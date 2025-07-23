# FinXray Backend

AI-powered startup risk analysis platform backend built with FastAPI.

## Quick Deploy to Render

### 1. Upload to GitHub:
- Create new repository: `finxray-backend`
- Upload all these files to the repository

### 2. Deploy on Render:
- Go to render.com
- Create "New Web Service"
- Connect your GitHub repository
- Use these settings:
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - **Runtime:** Python 3

### 3. Environment Variables:
Add these in Render dashboard:
- `SENDGRID_API_KEY` (for email alerts)
- `MONGODB_URI` (database connection)
- `JWT_SECRET_KEY` (authentication)

### 4. Connect to Frontend:
- Copy your Render backend URL
- In Vercel project settings, add: `NEXT_PUBLIC_API_URL = https://your-backend.onrender.com`

## API Endpoints

- `GET /` - Health check
- `POST /api/upload/analyze` - Analyze startup documents
- `POST /api/auth/login` - User authentication
- `POST /api/subscription/upgrade` - Upgrade to premium
- `GET /api/watchlist/{user_email}` - Get user watchlist

## Features

✅ FastAPI with automatic API docs at `/docs`
✅ File upload and OCR processing
✅ AI risk scoring with 4 risk categories
✅ Email alerts for high-risk startups
✅ Subscription management
✅ CORS enabled for frontend connection
✅ Production-ready with proper error handling

## File Structure

```
finxray-backend/
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── ocr.py                     # MCA filing processing
├── risk_model.py              # AI risk scoring engine
├── email_notifications.py     # SendGrid email integration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

Your frontend (HTML, CSS, JS) should be deployed separately on Vercel.

Blood Report Analyzer

Overview:

This FastAPI-based web service analyzes blood report PDFs, generates summaries with actionable recommendations, and sends relevant medical articles to users via email.

Setup

Installation:

Clone the repository:

    git clone https://github.com/deepxanshu/vwo-health-insight.git
    cd vwo-health-insight

Set up environment variables:

Create a .env file in the root directory:
    OPEN_AI_KEY="open_ai_key"
    SERPER_API_KEY="serper_api_key"
    SENDGRID_API_KEY="sendgrid_api_key"

Ensure the .env file contains required variables.

Install dependencies and start the server:

    pip install -r requirements.txt
    uvicorn src.main:app --reload

API Endpoints

Authentication

POST /token
Request:

    curl --location 'http://127.0.0.1:8000/token' \
    --form 'username="user@example.com"' \
    --form 'password="password"'
    Response:
    json
    Copy code
    {
        "access_token": "your_jwt_token",
        "token_type": "bearer"
    }

Analyze Report

POST /analyze
Request:
    curl --location 'http://127.0.0.1:8000/analyze' \
    --header 'Authorization: Bearer your_jwt_token' \
    --form 'file=@"/path/to/blood_report.pdf"' \
    --form 'email="your_email@example.com"'
    Response:
    json
    Copy code
    {
        "message": "Report analyzed and email sent successfully.",
        "articles": ["article_url1", "article_url2", ...]
    }
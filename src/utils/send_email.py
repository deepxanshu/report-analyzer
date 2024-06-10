import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_USERNAME = 'apikey' 
SENDGRID_PASSWORD = os.getenv("SENDGRID_API_KEY")


def send_email(to_email, analysis_result):
    from_email = 'deepanshuchaudharyy@gmail.com' 
    subject = 'Your Health Report Analysis'

    summary = analysis_result.get('summary', '')
    recommendations = analysis_result.get('recommendations', '')
    articles = analysis_result.get('articles', [])

    # HTML Template
    body = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 20px;
                color: #333;
            }}
            h1 {{
                color: #0056b3;
                text-align: center;
            }}
            p {{
                font-size: 14px;
                line-height: 1.5;
                text-align: justify;
            }}
            ul {{
                margin: 10px 0;
                padding: 0 20px;
            }}
            li {{
                margin-bottom: 10px;
                font-size: 14px;
                line-height: 1.5;
            }}
            a {{
                color: #007bff;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .content-box {{
                margin-bottom: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px 15px;
                background-color: #f9f9f9;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <h1>Your Health Report Analysis</h1>
        <div class="content-box">
            <h2>Summary</h2>
            <p>{summary}</p>
        </div>
        <div class="content-box">
            <h2>Recommendations</h2>
            <p>{recommendations}</p>
        </div>
        <div class="content-box">
            <h2>Useful Articles</h2>
            <ul>
    """

    for article in articles:
        body += f"<li><a href='{article}'>{article}</a></li>"

    body += """
            </ul>
        </div>
        <div class="footer">
            <p>For more information, please consult with your healthcare provider.</p>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP('smtp.sendgrid.net', 587) as server:
            server.starttls()
            server.login(SENDGRID_USERNAME, SENDGRID_PASSWORD)
            server.sendmail(from_email, to_email, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
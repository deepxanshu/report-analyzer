import httpx
import json
import os
import json
import logging
from typing import List
from dotenv import load_dotenv
from fastapi import HTTPException
from src.ai.ai import chat_completion_request
from src.utils.extract_pdf import extract_text_from_pdf

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
load_dotenv()


def analyze_pdf(pdf_file: bytes) -> any:
    try:
        blood_report_text = extract_text_from_pdf(pdf_file)
    except Exception as e:
        logger.error("Error extracting text from PDF: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")
    
    messages = [
        {"role": "system", "content": "You are a top-tier medical AI assistant. Analyze the following blood report and provide a concise and relevant summary. Make sure to highlight any abnormal findings and give actionable recommendations."},
        {"role": "user", "content": blood_report_text}
    ]

    functions = [
        {
            "name": "analyze_blood_report",
            "description": "Analyzes the blood report and provides a summary with actionable recommendations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "The summary of the blood report."},
                    "recommendations": {"type": "string", "description": "Actionable recommendations based on the blood report."}
                },
                "required": ["summary", "recommendations"]
            }
        }
    ]
    function_call = {"name": "analyze_blood_report"}

    try:
        logger.debug("Sending request to chat_completion_request with messages: %s", messages)
        chat_response = chat_completion_request(messages, functions=functions, function_call=function_call)
        logger.debug("Received response from chat_completion_request: %s", chat_response)
        assistant_message = chat_response.json()["choices"][0]["message"]
    except KeyError as e:
        logger.error("KeyError: %s", str(e))
        raise HTTPException(status_code=500, detail="Error processing the request.")
    except Exception as e:
        logger.error("Exception: %s", str(e))
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

    if assistant_message.get("function_call"):
        arguments = json.loads(assistant_message.get("function_call").get('arguments'))
        summary: str = arguments.get("summary") or "Summary generation failed"
        recommendations: str = arguments.get("recommendations") or "Recommendation generation failed"
        
        return {"summary": summary, "recommendations": recommendations}
    else:
        raise HTTPException(status_code=500, detail="Blood report analysis failed")
    
    
async def fetch_relevant_articles(summary: str, recommendation: str):
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise ValueError("SERPER_API_KEY environment variable not set")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }
    query = f"{summary} {recommendation}"
    payload = {
        "q": query,
        "gl": "in"
    }
    
    url = "https://google.serper.dev/search"
    
    try:
        async with httpx.AsyncClient(verify=False) as client:  # Disable SSL verification here
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Ensure response is JSON
            if "application/json" not in response.headers["Content-Type"]:
                raise HTTPException(status_code=500, detail="Invalid response format from Serper API")
            
            data = response.json()
            
            articles = data.get("organic", [])
            top_articles = articles[:4]  
            article_urls = [article['link'] for article in top_articles]

            return article_urls
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error fetching articles: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
async def analyze_report_and_fetch_articles(pdf_content: bytes):
    analysis_result = analyze_pdf(pdf_content)
    summary = analysis_result.get("summary")
    recommendations = analysis_result.get("recommendations")
    # FinancialAnalystCrew().crew().kickoff(inputs=pdf_content)
    

    if not summary or not recommendations:
        raise HTTPException(status_code=500, detail="Analysis result is incomplete.")

    articles = await fetch_relevant_articles(summary, recommendations)
    analysis_result["articles"] = articles
    return analysis_result
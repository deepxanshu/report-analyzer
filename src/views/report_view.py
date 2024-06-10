from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..config.auth import authenticate_user, create_access_token, get_current_user
from ..utils import send_email
from ..services import analyze_report_and_fetch_articles
# from ..crewai import crew

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    
@router.get("/")
def read_root():
    return {"message": "Service is running!"}

@router.post("/token", response_model=Token)
async def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/analyze")
async def analyze_report(file: UploadFile = File(...), email: str = Form(...), token: str = Depends(oauth2_scheme)):
    # user = get_current_user(token)
    pdf_content = await file.read()
    analysis_result = await analyze_report_and_fetch_articles(pdf_content)
    # analysis_result = crew.analyze_report_and_fetch_articles(pdf_content)
    
    send_email.send_email(email, analysis_result)
    return {"message": "Report analyzed and email sent successfully.",
            "articles": analysis_result.get("articles")
            }

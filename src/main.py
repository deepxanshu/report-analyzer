from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .views.report_view import router as report_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report_router)
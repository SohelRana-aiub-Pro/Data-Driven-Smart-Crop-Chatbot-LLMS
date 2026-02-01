#import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from fastapi.staticfiles import StaticFiles
from app.services import get_crop_advice, generate_tts
from app.config import SUPPORTED_LANGUAGES

app = FastAPI(title="Smart Crop Advisory Chatbot (Multilingual + Speech)")
templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "answer": None, "audio": None, "languages": SUPPORTED_LANGUAGES}
    )

@app.post("/advice", response_class=HTMLResponse)
def crop_advice(request: Request, crop: str = Form(...), question: str = Form(...), language: str = Form(...)):
    answer = get_crop_advice(crop, question, language)
    audio_file = generate_tts(answer, language)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "answer": answer, "audio": audio_file, "languages": SUPPORTED_LANGUAGES}
    )
#
"""AzHandwrite-Eval API. Run: python -m uvicorn app:app --reload"""
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from evaluation import alignment, word_error_rate
from ocr_service import recognize, review_language

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
app = FastAPI(title='AzHandwrite-Eval')
ALLOWED = {'image/png', 'image/jpeg', 'image/webp'}
MAX_BYTES = 8 * 1024 * 1024

class Comparison(BaseModel):
    prediction: str = Field(max_length=12000)
    reference: str = Field(max_length=12000)

class LanguageInput(BaseModel):
    text: str = Field(min_length=1, max_length=6000)

@app.get('/')
def index():
    return FileResponse(ROOT / 'index.html')

@app.get('/api/health')
def health():
    return {'status': 'ok', 'api_key_configured': bool(os.getenv('GEMINI_API_KEY'))}

@app.post('/api/ocr')
async def ocr(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=415, detail='Yalnız PNG, JPG, WEBP dəstəklənir.')
    image = await file.read(MAX_BYTES + 1)
    if not image:
        raise HTTPException(status_code=400, detail='Şəkil boşdur.')
    if len(image) > MAX_BYTES:
        raise HTTPException(status_code=413, detail='Şəkil 8 MB-dan böyükdür.')
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        raise HTTPException(status_code=503, detail='GEMINI_API_KEY yoxdur.')
    return await recognize(image, file.content_type, key)

@app.post('/api/evaluate')
def evaluate(item: Comparison):
    try:
        result = alignment(item.prediction, item.reference)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result['wer_percent'] = word_error_rate(item.prediction, item.reference)
    result['character_correctness_percent'] = round(max(0, 100 - result['cer_percent']), 2) if result['cer_percent'] is not None else None
    result['character_correctness_note'] = '100-CER (0-100 aralığına məhdudlaşdırılıb); müstəqil accuracy ölçüsü deyil.'
    return result

@app.post('/api/language-review')
async def language_review(item: LanguageInput):
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        raise HTTPException(status_code=503, detail='GEMINI_API_KEY yoxdur.')
    return await review_language(item.text, key)

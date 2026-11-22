AZHANDWRITE - AUTO CORRECTION + YELLOW HIGHLIGHTS

1. Copy all files into your project folder (do not overwrite your existing .env).
2. python -m pip install -r requirements.txt
3. python -m py_compile app.py ocr_service.py evaluation.py
4. python -m uvicorn app:app --reload
5. Open http://127.0.0.1:8000 and hard refresh Ctrl+F5.

The API returns raw_text, visual_text, corrected_text, correction_success.
The UI highlights the corrected_text relative to raw_text immediately.
CER is NOT calculated from AI correction alone; it requires verified ground truth.
The AI may be wrong and may time out; do not trust its corrections without checking.

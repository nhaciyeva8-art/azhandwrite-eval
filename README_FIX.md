AZHANDWRITE PATCH — 22 Nov 2026
1. Replace index.html and ocr_service.py with these files. Keep app.py and evaluation.py from the same package, or replace all four together.
2. Keep your local .env; never upload it.
3. Run: python -m pip install -r requirements.txt
4. Run: python -m py_compile app.py ocr_service.py evaluation.py
5. Run: python -m uvicorn app:app --reload
6. Open http://127.0.0.1:8000 and press Ctrl+F5.
7. Select a built-in sample, click AI ilə oxu, then Düzgün cavabı göstər. Highlight and CER appear against known sample reference.
8. For an uploaded image, AI düzəlişini göstər compares OCR vs AI second pass; if identical, NO yellow marks, and CER stays blank until user verifies the image transcription and saves.
9. Grammar suggestions are not ground truth and may be wrong. The AI service can return 503; this cannot be guaranteed away.
10. If the UI looks tiny, reset browser zoom with Ctrl+0.

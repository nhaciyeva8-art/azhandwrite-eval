# AzHandwrite-Eval — setup

Replace the project's `app.py` and `index.html`, and add `ocr_service.py`, `evaluation.py`, `requirements.txt`, `.gitignore`. Keep your own `.env` locally; NEVER upload it.

Windows PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m py_compile app.py ocr_service.py evaluation.py
python -m uvicorn app:app --reload
```

Open http://127.0.0.1:8000 and use Ctrl+F5 after updating frontend.

API endpoints:
- `POST /api/ocr` multipart `file`: raw OCR + visual review
- `POST /api/evaluate` JSON `{"prediction":"Azerbaycan", "reference":"Azərbaycan"}`: alignment, CER, WER
- `POST /api/language-review` JSON `{"text":"Mən məktəb gedirəm."}`: optional linguistic suggestions, not OCR ground truth
- `GET /api/health`

Reveal button: for built-in samples, shows the predefined example reference; for uploaded images, shows AI's proposal, NOT verified ground truth. CER appears only for an unchanged built-in sample reference or after user confirmation during save. The sample image is a generated canvas rendering; it is not a benchmark of real handwriting. Built-in dataset and model benchmark figures are demo values, not verified scientific measurements. An AI API outage can still prevent live OCR; sample mode is labeled as demo.

Accuracy claims require independently verified ground truth. CER can exceed 100% when the prediction has many insertions.

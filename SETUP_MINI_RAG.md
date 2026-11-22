# AzHandwrite-Eval — Mini-RAG + CER/WER

1. Bu qovluqdakı faylları layihə qovluğuna köçürün. `.env` faylını dəyişməyin.
2. `python -m pip install -r requirements.txt`
3. `python -m py_compile app.py ocr_service.py evaluation.py rag_service.py`
4. `python -m uvicorn app:app --reload`
5. Brauzerdə Ctrl+Shift+R.

**CER və WER yalnız etalon təsdiqlənəndə OCR keyfiyyət göstəricisidir.** `character_correctness_percent` = max(0, 100−CER); bu ayrıca statistik accuracy ölçüsü deyil. Etalon olmadıqda sarı dəyişikliklər AI təklifidir.

Mini-RAG: `language_rules.json` faylındakı qısa qaydalar açar sözlərlə seçilir; bu, internetdən canlı axtarış və ya tam rəsmi korpus deyil. `editorial_summary_unverified` qeydləri rəsmi sitat kimi göstərilməməlidir. `source_url` orfoqrafiya konteksti üçündür, konkret qrammatika maddəsinə istinad deyil.

Gemini cavablarının düzgünlüyü və servis əlçatanlığına zəmanət yoxdur. Tibbi əlyazmada qeyri-müəyyən dərman/doza avtomatik təsdiqlənməməlidir.

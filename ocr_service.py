"""Gemini handwriting recognition, visual recheck, optional language review."""
import asyncio
import logging
import os
from google import genai
from google.genai import types
from fastapi import HTTPException
from rag_service import build_context

logger = logging.getLogger('azhandwrite')
MODELS = ['gemini-3.1-flash-lite', 'gemini-3-flash-preview', 'gemini-3.8-flash']
TIMEOUT_SECONDS = 22

OCR_PROMPT = '''Transcribe Azerbaijani HANDWRITING from the attached image exactly as written.
Preserve the author's spelling mistakes, punctuation and Azerbaijani characters (ə, ğ, ı, İ, ö, ü, ş, ç).
Include handwritten heading. Do not infer missing text; use [oxunmur].
Reply ONLY with the first line ƏLYAZMA and subsequent lines transcription.
If no handwriting, reply first line DİGƏR followed by short description in Azerbaijani.'''
REVIEW_PROMPT = '''Independently re-read the attached image as an Azerbaijani handwriting specialist.
The draft OCR below is UNRELIABLE. Verify every glyph visually, especially ə/e, ş/s, ğ/g, ı/i, ö/o, ü/u, ç/c.
Correct ONLY errors in OCR compared with what is visibly handwritten. Do NOT correct spelling or grammar mistakes that exist on the paper.
Retain the heading, punctuation, and original word order. Use [oxunmur] for illegible spans.
Return ONLY the revised transcription (no label, no markdown).
Unreliable OCR draft:\n'''
LANGUAGE_PROMPT = """You are an Azerbaijani-language proofreader. This is NOT an OCR benchmark.
Do not assume the handwriting author intended standard spelling. Work ONLY with the given transcription.
Only report definite spelling/grammar errors. If uncertain, DO NOT flag them.
Never suggest corrections that are identical to the original.
Correct examples that MUST NOT be flagged: 'Xəzər dənizinin sahilində', 'Azərbaycanın inkişafı üçün', 'inkişafı', 'artırmağa'.
Do not claim that a correct genitive or possessive ending is missing.
If no definite error, return EXACTLY: Aydın orfoqrafik və ya qrammatik səhv aşkar edilmədi.
If there are definite errors, write the revised text and at most 3 short reasons; quote original and corrected form precisely.
Do not invent punctuation or grammar rules. No accuracy percentages.
TEXT:\n"""

async def request_model(client, prompt, image=None, mime=None, attempts=1):
    last_error = None
    for model in MODELS:
        for attempt in range(attempts):
            try:
                logger.info('AI model=%s attempt=%s', model, attempt+1)
                contents = [prompt]
                if image is not None:
                    contents.append(types.Part.from_bytes(data=image, mime_type=mime))
                response = await asyncio.wait_for(client.aio.models.generate_content(
                    model=model, contents=contents,
                    config=types.GenerateContentConfig(temperature=0)), timeout=TIMEOUT_SECONDS)
                answer = (response.text or '').strip()
                if answer:
                    return answer, model
                last_error = ValueError('Empty model response')
                break
            except asyncio.TimeoutError as exc:
                last_error = exc
                logger.warning('AI timeout model=%s', model)
            except Exception as exc:
                last_error = exc
                code = getattr(exc, 'code', None)
                logger.warning('AI failed model=%s status=%s', model, code)
                if code in (401, 403, 429):
                    raise HTTPException(status_code=429 if code == 429 else 503,
                        detail='API icazəsi və ya istifadə limiti problemi.') from exc
                if code in (400, 404):
                    break
                if code not in (500, 502, 503, 504):
                    break
            if attempt + 1 < attempts:
                await asyncio.sleep(1)
    raise HTTPException(status_code=503, detail='AI modelləri hazırda cavab vermir.') from last_error

CORRECT_PROMPT = """You are an expert Azerbaijani text editor. The text below is an OCR transcription of handwriting.
Produce a CLEAN, CORRECTED Azerbaijani text. Correct definite spelling, diacritics (ə, ı, ş, ğ, ö, ü, ç), punctuation and grammatical case suffix mistakes.
Preserve meaning, facts, names, order, and paragraphs. Do not add content or hallucinate illegible words. Keep [oxunmur] unchanged.
Check full sentence grammar, verb constructions and spelling. Example: "təhsil almağa və biliklərimi artırmağa istəyirəm" -> "təhsil almaq və biliklərimi artırmaq istəyirəm". Do not overgeneralize this example.
Use the retrieved language guidance below as optional reference, not as evidence that the OCR is wrong. Never invent citations.
If the input is already correct, return it unchanged. Return ONLY the full corrected text; no markdown, explanations or labels.
TEXT:\n"""

async def recognize(image, mime, key):
    client = genai.Client(api_key=key)
    try:
        first, model = await request_model(client, OCR_PROMPT, image, mime, attempts=2)
        header, sep, body = first.partition('\n')
        if sep and header.strip().upper() in ('ƏLYAZMA', 'DİGƏR'):
            kind = 'hw' if header.strip().upper() == 'ƏLYAZMA' else 'other'
            raw = body.strip()
        else:
            kind = 'hw'
            raw = first.strip()
        if not raw:
            raise HTTPException(status_code=502, detail='OCR boş mətn qaytardı.')
        visual, review_success, review_model = raw, False, None
        if kind == 'hw':
            try:
                review, review_model = await request_model(client, REVIEW_PROMPT + raw, image, mime)
                if review.strip():
                    visual = review.removeprefix('ƏLYAZMA\n').strip()
                    review_success = True
            except HTTPException:
                logger.warning('Visual review unavailable; raw OCR retained')
        rag_context, rag_rules = build_context(visual) if kind == 'hw' else ('', [])
        corrected, correction_success, correction_model = visual, False, None
        if kind == 'hw':
            try:
                candidate, correction_model = await request_model(client, CORRECT_PROMPT + "\nRETRIEVED RULES:\n" + rag_context + "\nINPUT TEXT:\n" + visual)
                if candidate.strip():
                    corrected = candidate.strip()
                    correction_success = True
            except HTTPException:
                logger.warning('Language correction unavailable; visual text retained')
        return {'kind': kind, 'text': raw, 'raw_text': raw,
                'visual_text': visual, 'corrected_text': corrected,
                'review_success': review_success, 'correction_success': correction_success,
                'model': model, 'review_model': review_model, 'correction_model': correction_model,
                'rag_rules': [{'id': r['id'], 'title': r['title'], 'source_url': r['source_url'], 'source_type': r['source_type']} for r in rag_rules]}

    finally:
        await client.aio.aclose()

async def review_language(text, key):
    client = genai.Client(api_key=key)
    try:
        rag_context, rag_rules = build_context(text)
        answer, model = await request_model(client, LANGUAGE_PROMPT + "\nRETRIEVED RULES:\n" + rag_context + "\nINPUT TEXT:\n" + text)
        return {'suggestion': answer, 'model': model, 'note': 'Dil təklifi OCR etalonu deyil.', 'rag_rules': [{'id': r['id'], 'title': r['title']} for r in rag_rules]}
    finally:
        await client.aio.aclose()

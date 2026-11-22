# AzHandwrite-Eval

**Azərbaycan dilində əlyazma mətnlərinin süni intellektlə tanınması, dil baxımından redaktəsi və OCR keyfiyyətinin qiymətləndirilməsi üçün prototip.**

Layihə açıq tipli əlyazma cavabların rəqəmsallaşdırılmasını asanlaşdırmaq, düzəlişləri görünən etmək və təsdiqlənmiş etalon mətn olduqda tanıma keyfiyyətini ölçmək məqsədi daşıyır. Əsas tətbiq sahələrinə təhsil və qiymətləndirmə prosesləri daxildir.

## İmkanlar

- **Əlyazmanın tanınması (OCR):** PNG, JPG və WEBP formatında şəkillər Gemini vizual dil modeli ilə oxunur.
- **İlkin və redaktə edilmiş mətn:** OCR transkripsiyası ayrıca saxlanılır; dil redaktəsi sonrakı mərhələdə aparılır.
- **Azərbaycan dili üzrə avtomatik düzəliş:** Orfoqrafiya, xüsusi hərflər, şəkilçilər və qrammatik konstruksiyalar yoxlanılır. AI-nin təklifləri mütləq düzgün hesab edilmir.
- **Mini-RAG:** `language_rules.json` faylındakı qısa qeydlər mətnə uyğun açar sözlər əsasında `rag_service.py` tərəfindən seçilir və dil redaktəsi sorğusuna əlavə olunur. Bu, vektor verilənlər bazası və ya canlı internet axtarışı deyil.
- **Dəyişikliklərin vizuallaşdırılması:** İlkin və düzəldilmiş mətn arasındakı fərqlər interfeysdə işarələnir.
- **CER və WER:** Etalon mətn daxil edildikdə simvol və söz səviyyəsində xəta göstəriciləri hesablanır.
- **Düzgünlük göstəricisi:** `max(0, 100 − CER)` — köməkçi göstəricidir, müstəqil statistik accuracy ölçüsü deyil.
- **Model fallback:** Bir model uğursuz olduqda digər konfiqurasiya edilmiş modellər sınaqdan keçirilə bilər; bu, API əlçatanlığına zəmanət vermir.

> **Vacib:** AI tərəfindən redaktə edilmiş mətn OCR üçün müstəqil etalon deyil. Real CER/WER hesablamaq üçün şəkildə yazılanları əks etdirən, insan tərəfindən yoxlanmış etalon transkripsiya tələb olunur. CER/WER şagirdin cavabının məzmununa verilən qiymət deyil.

## Texnologiyalar

| Hissə | Texnologiya |
|---|---|
| Backend | Python, FastAPI |
| AI/OCR | Google Gemini API (`google-genai`) |
| Mini-RAG | JSON qayda bazası, açar sözlə axtarış |
| Qiymətləndirmə | Levenshtein əsaslı CER/WER |
| Frontend | HTML, CSS, JavaScript |

## Quraşdırma

**Tələblər:** Python 3.11 və ya uyğun yeni versiya, Gemini API açarı.

1. Repository-ni klonlayın və layihə qovluğuna keçin:

   ```bash
   git clone <REPOSITORY_URL>
   cd <LAYIHE_QOVLUGU>
   ```

2. Virtual mühit yaradın və aktivləşdirin (Windows PowerShell):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Asılılıqları quraşdırın:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Layihə qovluğunda `.env` faylı yaradın:

   ```env
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   ```

   `.env` faylını GitHub-a yükləməyin. Açarı [Google AI Studio](https://aistudio.google.com/) vasitəsilə əldə etmək olar.

5. Sintaksisi yoxlayın və serveri başladın:

   ```bash
   python -m py_compile app.py ocr_service.py evaluation.py rag_service.py
   python -m uvicorn app:app --reload
   ```

6. Brauzerdə **http://127.0.0.1:8000** ünvanını açın.

## İstifadə qaydası

1. Əlyazma şəkli yükləyin və ya hazır nümunə seçin.
2. OCR nəticəsini və AI-nin təklif etdiyi redaktə edilmiş mətni müqayisə edin.
3. İşarələnmiş dəyişiklikləri yoxlayın.
4. Etalon transkripsiya mövcuddursa, CER/WER hesablayın.
5. Nəticələri insan nəzarəti ilə təsdiqləyin.

## API endpoint-ləri

| Metod | Ünvan | Təyinat |
|---|---|---|
| `GET` | `/` | Veb interfeys |
| `GET` | `/api/health` | Server və API açarının konfiqurasiya statusu |
| `POST` | `/api/ocr` | Şəkildən mətnin tanınması və redaktə təklifi |
| `POST` | `/api/evaluate` | Proqnoz və etalon üzrə CER/WER |
| `POST` | `/api/language-review` | Mətn üzrə dil yoxlaması |

**Qiymətləndirmə sorğusu nümunəsi:**

```json
{
  "prediction": "Azerbaycan",
  "reference": "Azərbaycan"
}
```

`/api/ocr` üçün `multipart/form-data` formatında `file` sahəsi göndərilir. Maksimum fayl ölçüsü **8 MB**-dır.

## Layihə strukturu

```text
AzHandwrite-Eval/
├── app.py                 # FastAPI endpoint-ləri
├── ocr_service.py         # Gemini OCR və AI dil redaktəsi
├── rag_service.py         # Mini-RAG qayda axtarışı
├── language_rules.json    # Dil qaydaları üzrə qısa qeydlər
├── evaluation.py          # CER/WER və mətn uyğunlaşdırılması
├── index.html             # Veb interfeys
├── requirements.txt       # Python asılılıqları
├── .env.example           # Konfiqurasiya nümunəsi
└── README.md
```

## Məhdudiyyətlər və təhlükəsizlik

- Gemini API-də **429**, **502**, **503** və timeout xətaları mümkündür; fallback bütün hallarda problemi həll etmir.
- Mini-RAG qaydaları tam, təsdiqlənmiş Azərbaycan dili korpusu deyil. Qrammatik xülasələr konkret rəsmi maddəyə istinad kimi təqdim edilməməlidir.
- Dil redaktəsi müəllimin və ya mütəxəssisin yoxlamasını əvəz etmir.
- Əlyazmada şəxsi və ya həssas məlumatlar varsa, üçüncü tərəf AI xidmətinə göndərməzdən əvvəl məlumatların qorunması tələblərini nəzərə alın.
- Cavabın **məzmun üzrə rubrika ilə avtomatik ballanması** hazırkı OCR/CER funksiyasından ayrıdır və ayrıca inkişaf mərhələsidir.

## Gələcək inkişaf

- Daha geniş, mənbəsi təsdiqlənmiş Azərbaycan dili qayda bazası.
- Təsdiqlənmiş əlyazma–etalon cütləri ilə qiymətləndirmə dəsti.
- Müxtəlif OCR modellərinin eyni test dəsti üzrə müqayisəsi.
- Müəllim təsdiqi və rubrika əsasında məzmun qiymətləndirməsi.
- Təqdimat üçün etibarlılıq, gecikmə və API xəta testləri.

## Komanda

- **Məryəm Quliyeva** — dilçilik, etalon korpus və qiymətləndirmə meyarları
- **Əhmədnuri Əlizadə** — data və sistem/AI arxitekturası
- **Nəzrin Hacıyeva** — frontend və prototip inkişafı
- **Xəlil Xudayev** — ideya müəllifi və AI yaradıcı həlləri
- **Aysel Musayeva** — AI inteqrasiyası, model qiymətləndirməsi və test analitikası

## Mənbələr

- [Azərbaycan dilinin Orfoqrafiya Normaları — e-qanun](https://e-qanun.az/framework/42073)
- [Google Gemini API sənədləri](https://ai.google.dev/gemini-api/docs)
- [Google Gemini API xəta diaqnostikası](https://ai.google.dev/gemini-api/docs/troubleshooting)
- [FastAPI sənədləri](https://fastapi.tiangolo.com/)
- [Levenshtein məsafəsi](https://rapidfuzz.github.io/Levenshtein/)

---

**Qeyd:** Layihə prototip mərhələsindədir. Demo və API funksiyalarını istifadədən əvvəl real şəkillərlə yoxlamaq tövsiyə olunur.

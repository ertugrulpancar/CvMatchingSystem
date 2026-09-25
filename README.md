# CV ↔ İlan Eşleştirme Sistemi

Yeni mezunlar için web uygulaması. Kullanıcı Google ile giriş yapar, CV'sini (PDF/DOCX yükleme veya
metin yapıştırma) ve bir iş ilanı metnini verir. Uygulama ilanı yapılandırılmış gereksinimlere ayırır,
her gereksinim için CV'de karşılığı olup olmadığını CV'den birebir alıntıyla belirler, ağırlıklı
ortalama ile bir uyum skoru hesaplar ve sonucu kullanıcının geçmişine kaydeder.

## Mimari

```
frontend/   React + Vite + TypeScript — Vercel projesi #1
backend/    FastAPI (Python) — Vercel projesi #2, Supabase Postgres'e bağlanır
```

- Kimlik doğrulama: Supabase Auth, yalnızca Google OAuth.
- LLM: Google Gemini (`google-genai`), yapılandırılmış çıktı ile.
- Skor kod tarafında hesaplanır, LLM skoru asla üretmez.
- CV'nin tam metni veya dosyası hiçbir zaman saklanmaz.

## Yerel geliştirme

### Ön koşullar

- Python ≥ 3.12, [uv](https://docs.astral.sh/uv/)
- Node.js ≥ 20, npm
- Bir [Supabase](https://supabase.com) projesi (ücretsiz plan yeterli)
- Bir [Google Gemini API anahtarı](https://aistudio.google.com/apikey) (ücretsiz)
- Google Cloud Console'da bir OAuth 2.0 Client ID (Supabase Google girişi için)

### Backend

```bash
cd backend
cp .env.example .env   # değerleri doldurun (aşağıya bakın)
uv sync
uv run alembic upgrade head   # MIGRATION_DATABASE_URL kullanır (session pooler :5432)
uv run uvicorn app.main:app --reload   # http://localhost:8000
```

`backend/.env` içinde doldurulması gerekenler:

| Değişken | Nereden alınır |
|---|---|
| `GEMINI_API_KEY`, `GEMINI_MODEL` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `MATCHER` | `llm` (gerçek Gemini) veya `keyword` (API anahtarı gerektirmeyen yedek) |
| `DATABASE_URL` | Supabase → Project Settings → Database → Connect → ORM → Transaction pooler (**:6543**) |
| `MIGRATION_DATABASE_URL` | Aynı yer → Session pooler (**:5432**), sadece `alembic` için |
| `SUPABASE_URL` | Supabase → Project Settings → API |
| `ALLOWED_ORIGINS` | Lokal: `http://localhost:5173` |

Testler gerçek Gemini'ye veya gerçek veritabanına bağlanmaz:

```bash
uv run pytest
uv run ruff check . && uv run ruff format .
```

### Frontend

```bash
cd frontend
cp .env.example .env   # değerleri doldurun (aşağıya bakın)
npm install
npm run dev   # http://localhost:5173, /api isteklerini backend'e proxy'ler
```

`frontend/.env` içinde doldurulması gerekenler:

| Değişken | Nereden alınır |
|---|---|
| `VITE_SUPABASE_URL` | Supabase → Project Settings → API |
| `VITE_SUPABASE_ANON_KEY` | Supabase → Project Settings → API (publishable/anon key — herkese açık olması güvenlidir, RLS deny-all korur) |
| `VITE_API_BASE_URL` | Lokal: boş bırakın (Vite proxy kullanılır) |

Backend şeması değiştiyse tipleri yeniden üretin (backend `:8000`'de çalışırken):

```bash
npm run gen:types
```

### Google OAuth kurulumu (özet)

1. Google Cloud Console → OAuth consent screen (External) → test kullanıcısı olarak kendi
   hesabınızı ekleyin.
2. Credentials → OAuth client ID → Web application:
   - Authorized JavaScript origins: `http://localhost:5173` (+ prod frontend URL'i)
   - Authorized redirect URIs: `<SUPABASE_URL>/auth/v1/callback`
3. Supabase Dashboard → Authentication → Providers → Google: Client ID/Secret'ı girin.
4. Supabase Dashboard → Authentication → URL Configuration: Site URL ve Redirect URLs'e
   frontend adresini ekleyin.

## Deploy (Vercel)

Aynı GitHub reposundan iki ayrı Vercel projesi oluşturulur, her birinin Root Directory'si kendi
klasörüne (`backend/`, `frontend/`) ayarlanır. Ortam değişkenleri her iki projede de ilgili
`.env.example` dosyasındakilerle aynıdır; `VITE_API_BASE_URL` prod backend'in Vercel URL'i,
backend'in `ALLOWED_ORIGINS`'i de prod frontend'in Vercel URL'i olmalıdır.

`backend/vercel.json`, fonksiyon süresini 60 saniyeye çıkarır ve `tests/`/`alembic/` klasörlerini
deploy paketinden hariç tutar.

## Testler

```bash
cd backend && uv run pytest
cd frontend && npx tsc -b && npm run lint
```

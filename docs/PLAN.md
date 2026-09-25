# CV Matching System — Proje Planı

> **Bu doküman kimin için?** Kodlama aşamasını yürütecek geliştirici (insan veya AI) için tek referans kaynağıdır.
> Fazlar sırayla uygulanır. Her faz sonunda "Bitti kriteri" sağlanmadan sonraki faza geçilmez.
> Proje eğitim amaçlıdır: her faz sonunda alınan önemli tasarım kararları kısaca **"neden"** ile birlikte açıklanmalıdır.

---

## 0. Ürün Özeti

Yeni mezunlar için web uygulaması. Kullanıcı Google ile giriş yapar, CV'sini (PDF/DOCX yükleme veya metin yapıştırma) ve bir iş ilanı metnini verir. Uygulama:

1. İlanı yapılandırılmış gereksinimlere ayırır (zorunlu / tercih sebebi, kategori).
2. Her gereksinim için CV'de karşılığı olup olmadığını **CV'den birebir alıntıyla (evidence)** belirler.
3. Ağırlıklı ortalama ile **% uyum skoru** hesaplar ("bu ilana ne kadar uyumluyum").
4. Karşılanan / kısmi / eksik gereksinimleri listeler.
5. Analizi kullanıcının geçmişine kaydeder (CV'nin tam metni ve dosyası **saklanmaz**).

**Kesinleşmiş kararlar:**

| Konu | Karar |
|---|---|
| Dil | CV ve ilan TR veya EN olabilir, çapraz eşleşme (TR CV ↔ EN ilan ve tersi) desteklenir |
| Arayüz dili | TR/EN seçimli. `explanation` alanları seçilen arayüz dilinde üretilir |
| LLM | Google Gemini (`google-genai` SDK), structured output |
| Skor | Ağırlıklı ortalama. must_have=2, nice_to_have=1, met=1.0, partial=0.5, missing=0 |
| Veritabanı | Supabase (Postgres) |
| Auth | Supabase Auth, yalnızca Google OAuth. **Analiz için giriş zorunlu** |
| Saklanan veri | Analiz sonucu + ilan metni. CV tam metni ve dosyası saklanmaz |
| Deploy | Vercel, aynı repodan iki proje (frontend ve backend) |
| Frontend | React + Vite + TypeScript |

---

## 1. Mimari

```
┌──────────────────────────┐                          ┌──────────────────────────────────────────────┐
│ Frontend (Vercel #1)     │   Bearer <Supabase JWT>  │ Backend: FastAPI (Vercel #2, serverless)      │
│ React + Vite + TS        │ ───────────────────────▶ │                                              │
│  - Google login          │                          │ api/        ince HTTP katmanı + auth dep.     │
│    (supabase-js, sadece  │ ◀─────────────────────── │   │                                           │
│     auth için)           │      JSON               │   ▼                                           │
│  - Yeni analiz           │                          │ services/                                     │
│  - Geçmiş / detay        │                          │   parsing    PDF/DOCX → metin                 │
└───────────┬──────────────┘                          │   llm        Gemini çağrıları        ─────────┼──▶ Gemini API
            │ OAuth                                   │   matching   Matcher (Strategy)               │
            ▼                                         │   scoring    saf fonksiyon                    │
     Supabase Auth ◀── JWKS ile JWT doğrulama ─────── │   analysis_service  orkestratör               │
                                                      │ repositories/  AnalysisRepository  ──────────┼──▶ Supabase Postgres
                                                      └──────────────────────────────────────────────┘     (Supavisor pooler :6543)
```

**Temel kararlar ve gerekçeleri:**

- **Frontend veritabanına doğrudan erişmez, yalnızca FastAPI'ye erişir.** `supabase-js` frontend'de sadece Google girişi ve oturum için kullanılır. İş mantığı ve veri erişimi tek bir yerde (backend) toplanır. Böylece güvenlik kuralları iki yerde (RLS + backend) tekrar yazılmaz.
- **RLS yine de açık ve politikasız (deny-all).** Supabase, tabloları `anon key` ile PostgREST üzerinden otomatik olarak dışarı açar. RLS kapalı kalırsa anon key'i bilen herkes (key frontend'de herkese açık) tüm analizleri okuyabilir. Backend `postgres` rolüyle bağlandığı için RLS'ten etkilenmez. Bu, katmanlı savunma (defense in depth) ilkesidir.
- **Skoru LLM değil kod hesaplar.** LLM anlam gerektiren işi yapar (gereksinim çıkarma, CV'de karşılık bulma), kod kural gerektiren işi yapar (skor). Aynı yargılardan hep aynı skor çıkar ve skor açıklanabilir olur.
- **Strategy + Repository pattern.** `Matcher` (LLM / Keyword) ve `AnalysisRepository` (SQL / InMemory) arayüzleri sayesinde testler API anahtarı ve veritabanı olmadan çalışır.

---

## 2. Klasör Yapısı

```
CvMatchingSystem/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, CORS, router kaydı (Vercel entrypoint: app/main.py → app)
│   │   ├── core/
│   │   │   ├── config.py              # pydantic-settings ile .env okuma
│   │   │   ├── auth.py                # get_current_user dependency (JWT doğrulama)
│   │   │   └── db.py                  # SQLAlchemy engine/session (NullPool)
│   │   ├── api/routes/
│   │   │   ├── health.py
│   │   │   ├── documents.py           # POST /documents/parse
│   │   │   └── analyses.py            # POST/GET/DELETE /analyses
│   │   ├── schemas/                   # API sözleşmesi (Pydantic)
│   │   │   ├── document.py
│   │   │   ├── requirement.py
│   │   │   └── analysis.py
│   │   ├── models/                    # SQLAlchemy ORM modelleri (DB şeması)
│   │   │   └── analysis.py
│   │   ├── repositories/
│   │   │   ├── base.py                # AnalysisRepository Protocol
│   │   │   ├── sql_repository.py
│   │   │   └── memory_repository.py   # testler için
│   │   └── services/
│   │       ├── parsing/
│   │       │   ├── __init__.py        # parse_document(filename, bytes) → ParsedDocument
│   │       │   ├── pdf_parser.py      # pdfplumber
│   │       │   └── docx_parser.py     # python-docx
│   │       ├── llm/
│   │       │   ├── client.py          # Gemini'ye tek giriş noktası
│   │       │   ├── prompts.py
│   │       │   └── schemas.py         # LLM'e verilen/LLM'den dönen şemalar (API şemalarından ayrı)
│   │       ├── matching/
│   │       │   ├── base.py            # Matcher Protocol
│   │       │   ├── llm_matcher.py
│   │       │   ├── keyword_matcher.py
│   │       │   └── skills_dictionary.py   # iki dilli alias sözlüğü
│   │       ├── text_normalization.py  # normalize_for_match(), evidence doğrulama
│   │       ├── scoring.py             # saf fonksiyonlar
│   │       └── analysis_service.py    # parse → extract → match → verify → score → save
│   ├── alembic/                       # DB migration'ları
│   ├── alembic.ini
│   ├── tests/
│   │   ├── fixtures/                  # cv_tr.pdf, cv_en.docx, job_tr.txt, job_en.txt ...
│   │   ├── test_parsing.py
│   │   ├── test_text_normalization.py
│   │   ├── test_scoring.py
│   │   ├── test_keyword_matcher.py
│   │   └── test_api.py
│   ├── pyproject.toml
│   ├── vercel.json
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts              # fetch sarmalayıcı, Authorization header ekler
│   │   │   └── schema.d.ts            # openapi-typescript ile ÜRETİLİR, elle düzenlenmez
│   │   ├── lib/supabase.ts            # supabase-js client (sadece auth)
│   │   ├── i18n/                      # tr.json, en.json
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── NewAnalysisPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   └── AnalysisDetailPage.tsx
│   │   ├── components/
│   │   │   ├── CvInput.tsx            # dosya yükle / metin yapıştır
│   │   │   ├── JobInput.tsx
│   │   │   ├── ScoreCard.tsx
│   │   │   └── RequirementList.tsx
│   │   ├── App.tsx                    # router + korumalı rotalar
│   │   └── main.tsx
│   ├── vite.config.ts                 # /api → localhost:8000 proxy
│   ├── package.json
│   └── .env.example
├── docs/PLAN.md
├── .gitignore
└── README.md
```

**Neden `llm/schemas.py`, `schemas/`'tan ayrı?** LLM'in ürettiği yapı ile API'nin döndürdüğü yapı zamanla birbirinden ayrışır. Örneğin API'de `id` ve `created_at` alanları var, LLM bunları üretmez. Ayrıca Gemini'nin `response_schema` özelliği JSON Schema'nın yalnızca bir alt kümesini destekler (varsayılan değerler ve karmaşık union tipleri sorun çıkarabilir). Ayrı tutunca biri değiştiğinde diğeri bozulmaz.

**Neden `models/` (ORM) ve `schemas/` (Pydantic) ayrı?** Veritabanı tablosu ile API yanıtı aynı şey değil. Örneğin kategori skorları DB'de saklanmaz, okunurken hesaplanır. Bu ayrım tüm FastAPI projelerinde standarttır.

---

## 3. Veri Modeli

### 3a. API şemaları (Pydantic)

```python
class ParsedDocument(BaseModel):
    text: str
    source: Literal["pdf", "docx", "text"]
    char_count: int
    page_count: int | None = None

class RequirementCategory(str, Enum):
    TECHNICAL_SKILL = "technical_skill"
    TOOL = "tool"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    LANGUAGE = "language"
    SOFT_SKILL = "soft_skill"

class Importance(str, Enum):
    MUST_HAVE = "must_have"
    NICE_TO_HAVE = "nice_to_have"

class MatchStatus(str, Enum):
    MET = "met"
    PARTIAL = "partial"
    MISSING = "missing"

class RequirementMatch(BaseModel):
    requirement_text: str           # ilanın orijinal dilinde
    category: RequirementCategory
    importance: Importance
    status: MatchStatus
    evidence: str | None            # CV'den BİREBİR alıntı, orijinal dilde
    explanation: str                # output_language dilinde

class CategoryScore(BaseModel):
    category: RequirementCategory
    score: int                      # 0-100

class AnalysisResult(BaseModel):
    id: UUID
    created_at: datetime
    job_title: str | None           # LLM ilandan çıkarır, geçmiş listesinde gösterilir
    company_name: str | None
    overall_score: int              # 0-100
    category_scores: list[CategoryScore]   # DB'de saklanmaz, matches'tan hesaplanır
    matches: list[RequirementMatch]
    output_language: Literal["tr", "en"]
    matcher: Literal["llm", "keyword"]

class AnalysisSummary(BaseModel):   # geçmiş listesi için hafif model
    id: UUID
    created_at: datetime
    job_title: str | None
    company_name: str | None
    overall_score: int
```

Eksik listesi ayrı bir alan **değildir**. Frontend `matches` listesini `status == "missing"` ile filtreler. Tek doğruluk kaynağı (single source of truth) böyle korunur.

### 3b. Veritabanı şeması (Postgres / Supabase)

```sql
create table public.analyses (
  id              uuid primary key default gen_random_uuid(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  created_at      timestamptz not null default now(),
  job_title       text,
  company_name    text,
  job_text        text not null,
  cv_source       text not null check (cv_source in ('pdf','docx','text')),
  overall_score   smallint not null check (overall_score between 0 and 100),
  output_language text not null check (output_language in ('tr','en')),
  matcher         text not null check (matcher in ('llm','keyword')),
  model           text,
  duration_ms     integer not null
);
create index analyses_user_created_idx on public.analyses (user_id, created_at desc);

create table public.analysis_items (
  id               uuid primary key default gen_random_uuid(),
  analysis_id      uuid not null references public.analyses(id) on delete cascade,
  position         smallint not null,
  requirement_text text not null,
  category         text not null check (category in ('technical_skill','tool','experience','education','language','soft_skill')),
  importance       text not null check (importance in ('must_have','nice_to_have')),
  status           text not null check (status in ('met','partial','missing')),
  evidence         text,
  explanation      text not null
);
create index analysis_items_analysis_idx on public.analysis_items (analysis_id);

alter table public.analyses       enable row level security;
alter table public.analysis_items enable row level security;
-- Politika YOK: anon/authenticated rolleri PostgREST üzerinden hiçbir şey okuyamaz/yazamaz.
```

**Tasarım kararları:**

- **Gereksinim ve eşleşme tek tabloda (`analysis_items`).** Bir analiz içinde her gereksinimin tam olarak bir eşleşmesi var (1:1) ve gereksinimler analizden bağımsız yaşamıyor. Bunları iki tabloya bölmek gereksiz bir JOIN getirirdi (erken normalizasyon).
- **Neden JSONB yerine ayrı tablo?** Tüm eşleşmeleri `analyses` içinde tek bir JSONB kolonunda tutmak daha basit olurdu. Ayrı tablo sayesinde "geçmişimde en sık eksik çıkan beceriler" gibi SQL sorguları yazılabilir. Bu hem ileride bir özelliğe dönüşebilir hem de ilişkisel modellemeyi öğretir.
- **`overall_score` saklanıyor ama `category_scores` saklanmıyor.** Genel skor geçmiş listesinde her satırda gösterildiği için saklanıyor (bilinçli denormalizasyon). Ayrıca skor formülü ileride değişirse eski analizler o günkü skorlarını korur. Kategori skorları yalnızca detay sayfasında gerekiyor ve `analysis_items` üzerinden kolayca hesaplanabiliyor.
- **Postgres `ENUM` tipi yerine `text + CHECK`.** Postgres enum'una değer eklemek migration'larda zahmetlidir. CHECK constraint'i değiştirmek ise tek satırdır.
- **`on delete cascade` → `auth.users`.** Kullanıcı hesabı silinince tüm verisi de silinir (KVKK silme hakkı).
- **CV tam metni saklanmaz.** Yalnızca `evidence` alıntıları saklanır. Bunlar CV'den kısa parçalar olduğu için kişisel veri sayılır, bu yüzden erişim her zaman `user_id` ile sınırlanır.

---

## 4. API Endpoint'leri

Tüm `/api/v1/*` endpoint'leri `Authorization: Bearer <supabase_access_token>` ister. Token yoksa veya geçersizse `401` döner.

| Metot | Yol | Girdi | Çıktı |
|---|---|---|---|
| GET | `/api/health` | – | `{"status":"ok"}` (auth yok) |
| POST | `/api/v1/documents/parse` | multipart: `file` | `ParsedDocument` |
| POST | `/api/v1/analyses` | multipart: `cv_file` **veya** `cv_text`, `job_text`, `output_language` (`tr`/`en`) | `AnalysisResult` (201) |
| GET | `/api/v1/analyses?limit=20&before=<iso-datetime>` | – | `list[AnalysisSummary]` |
| GET | `/api/v1/analyses/{id}` | – | `AnalysisResult` |
| DELETE | `/api/v1/analyses/{id}` | – | 204 |

**Hata sözleşmesi:**

| Kod | Durum |
|---|---|
| 400 | Hem `cv_file` hem `cv_text` verildi, ya da ikisi de verilmedi |
| 401 | Token yok veya geçersiz |
| 404 | Analiz yok **veya başka kullanıcıya ait** (403 dönülmez, kaydın varlığı sızdırılmaz) |
| 413 | Dosya > 4 MB (Vercel'in 4.5 MB istek gövdesi sınırının altında kalmak için) |
| 415 | PDF/DOCX dışı format |
| 422 | Dosyadan metin çıkarılamadı (taranmış PDF) → kullanıcıya metni yapıştırması önerilir. CV > 20.000 veya ilan > 10.000 karakter. İlandan hiç gereksinim çıkarılamadı |
| 429 | Günlük analiz kotası aşıldı |
| 502 | Gemini hata verdi veya geçersiz yanıt döndü |

**Sayfalama:** `offset` yerine `before=<created_at>` kullanılır (keyset/cursor pagination). Offset sayfalamada araya yeni kayıt eklendiğinde kayma olur ve büyük offset değerleri yavaştır. Oluşturduğumuz `(user_id, created_at desc)` index'i keyset sayfalamayla doğrudan kullanılır.

**Günlük kota:** `select count(*) from analyses where user_id = :uid and created_at > now() - interval '1 day'` ≥ `DAILY_ANALYSIS_LIMIT` (varsayılan 20) ise 429 döner. Serverless ortamda bellek içi sayaç işe yaramaz, çünkü her istek farklı bir instance'a gidebilir. Veritabanı ise tüm instance'lar tarafından paylaşılır. Giriş zorunlu olduğu için kota kullanıcı başına uygulanabilir.

---

## 5. Eşleştirme Pipeline'ı

```
job_text ──▶ [LLM 1: extract] ──▶ JobExtraction{job_title, company_name, requirements[]}
                                              │
cv_text  ──────────────────────────▶ [LLM 2: match] ──▶ matches[] (status, evidence, explanation)
                                              │
                                   [verify_evidence]  (kod)
                                              │
                                   [scoring]  (kod) ──▶ overall_score, category_scores
```

### 5a. Parse
- PDF: `pdfplumber` (MIT lisansı, çok sütunlu CV'lerde iyi sonuç verir). **PyMuPDF kullanılmaz: AGPL lisansı.**
- DOCX: `python-docx`. Paragraflar ve tablo hücreleri birlikte okunur (birçok CV şablonu tablo kullanır).
- Çıkan metin 50 karakterden kısaysa taranmış PDF kabul edilir ve 422 döner.

### 5b. LLM çağrıları (Gemini)
- SDK: `google-genai`. `response_mime_type="application/json"` ve `response_schema=<Pydantic model>` ile structured output alınır.
- Model adı `GEMINI_MODEL` env değişkeninden okunur. Flash sınıfı bir modelle başlanır.
- **Prompt kuralları (`prompts.py`):**
  - İlan ve CV farklı dillerde olabilir. Eşleştirme dilden bağımsız, anlama göre yapılır ("makine öğrenmesi" = "machine learning").
  - `requirement_text` ilanın orijinal dilinde kalır.
  - `evidence` CV'den **birebir ve orijinal dilinde** alıntılanır, çevrilmez, en fazla ~200 karakter. Kanıt yoksa `null` olur.
  - `explanation` `{output_language}` dilinde, en fazla 1–2 cümle.
  - `met` = açıkça karşılanıyor, `partial` = ilgili ama eksik (örn. "3 yıl" isteniyor, CV'de 1 yıl var), `missing` = yok.
  - CV ve ilan metni prompt'ta `<cv>...</cv>` ve `<job_posting>...</job_posting>` etiketleri içine konur. Talimat olarak değil, **veri** olarak ele alınmaları istenir (prompt injection'a karşı).
- **Neden tek çağrı değil de iki çağrı?** Tek çağrı daha hızlı ve ucuz olurdu. İki çağrı ise her adımın ayrı test edilmesini, ayrı debug edilmesini sağlar. Ayrıca extraction çıktısı `KeywordMatcher` ile de kullanılabilir. Gecikme sorun olursa birleştirmek kolay.

### 5c. Evidence doğrulama (`text_normalization.py`)
LLM'in uydurduğu alıntıları yakalamak için:
```python
def normalize_for_match(s: str) -> str:
    # NFKC → casefold → U+0307 (birleşik nokta) sil → 'ı' → 'i' → boşlukları tek boşluğa indir
```
- **Neden gerekli?** `"İSTANBUL".lower()` Python'da `"i̇stanbul"` üretir (i + görünmez U+0307). Normalize edilmeden yapılan karşılaştırmalar Türkçe metinde sessizce başarısız olur.
- PDF metnindeki satır kırılmaları ve tirelemeler için `rapidfuzz.fuzz.partial_ratio(norm(evidence), norm(cv_text)) >= 90` eşiği kullanılır.
- Doğrulama başarısız olursa `met` → `partial` yapılır, `evidence` → `null` olur.
- **Test zorunlu:** Türkçe büyük/küçük harf, İngilizce "I", satır kırılması ve uydurma alıntı senaryoları.

### 5d. Skor (`scoring.py`, saf fonksiyon)
```
weight:  must_have = 2, nice_to_have = 1
points:  met = 1.0, partial = 0.5, missing = 0
overall = round( Σ(weight × points) / Σ(weight) × 100 )
```
Kategori skorları aynı formülle, yalnızca o kategorinin öğeleri üzerinden hesaplanır. Ağırlıklar ve puanlar `config.py`'dan okunur. Gereksinim listesi boşsa hata fırlatılır (sıfıra bölme olmaz, API 422 döner).

### 5e. KeywordMatcher (API anahtarı gerektirmeyen yedek eşleştirici)
- `skills_dictionary.py`: ~50 kayıt, `{"canonical": "Machine Learning", "category": "technical_skill", "aliases": ["ml", "makine öğrenmesi", "makine öğrenimi"]}`.
- İlanda bulunan becerileri gereksinim olarak alır. Hepsi `must_have` kabul edilir. CV'de alias'lardan biri geçiyorsa `met`, geçmiyorsa `missing` olur.
- `MATCHER=keyword|llm` env değişkeniyle seçilir. Testler ve API anahtarı olmadan yapılan geliştirme bu eşleştiriciyle çalışır.

---

## 6. Auth Akışı

1. Frontend: `supabase.auth.signInWithOAuth({ provider: "google" })`. Supabase oturumu yönetir.
2. Frontend her API isteğinde `Authorization: Bearer ${session.access_token}` header'ını gönderir.
3. Backend `core/auth.py` içinde `get_current_user` FastAPI dependency'si:
   - JWT'yi Supabase JWKS ile doğrular: `PyJWT` + `PyJWKClient("{SUPABASE_URL}/auth/v1/.well-known/jwks.json")`, `audience="authenticated"`.
   - `sub` claim'ini `user_id` (UUID) olarak döndürür.
   - Supabase projesi hâlâ eski HS256 JWT secret kullanıyorsa: Supabase dashboard'dan asimetrik JWT signing key'lere geçilir (önerilen) veya `SUPABASE_JWT_SECRET` ile HS256 doğrulaması yapılır.
4. Testlerde `app.dependency_overrides[get_current_user]` ile sahte kullanıcı verilir.

**Neden Dependency Injection?** Route fonksiyonları `user_id: UUID = Depends(get_current_user)` şeklinde kullanıcıyı parametre olarak alır. Auth mantığı tek yerde durur ve testlerde tek satırla değiştirilebilir.

---

## 7. Veritabanı Erişimi

- **SQLAlchemy 2.0 (sync) + Alembic + `psycopg` (v3).**
  - **Neden `supabase-py` değil?** SQLAlchemy ve Alembic sektör standardı ve Supabase'e bağımlı değil (herhangi bir Postgres'e taşınabilir). Migration'lar kodla birlikte versiyonlanır ve gerçek SQL/ORM öğrenilir.
  - **Neden sync?** FastAPI sync `def` endpoint'leri threadpool'da çalıştırır. Bu ölçekte async'in getirdiği karmaşıklığa değmez.
- **Serverless bağlantı kuralları (kritik):**
  - `DATABASE_URL` = Supabase **Supavisor transaction pooler**, port **6543**. Doğrudan 5432 portu değil, çünkü her serverless instance ayrı bağlantı açar ve Postgres bağlantı limiti hızla dolar.
  - `create_engine(..., poolclass=NullPool)`: Havuzlamayı Supavisor yapar, uygulama tarafında ikinci bir havuz olmaz.
  - Transaction pooler prepared statement desteklemez: `connect_args={"prepare_threshold": None}`.
- **Migration'lar:**
  - `public` şemasının tek sahibi Alembic'tir. Supabase dashboard'dan tablo oluşturulmaz.
  - `auth.users`'a yapılan FK ve `enable row level security` komutları migration içinde `op.execute(...)` ile yazılır.
  - Alembic `upgrade` işlemi Supavisor **session** pooler (port 5432) veya doğrudan bağlantı üzerinden çalıştırılır. Migration'lar transaction pooler'da sorun çıkarabilir, bu yüzden env'de ayrı bir `MIGRATION_DATABASE_URL` tutulur.
- **Kayıt işlemi:** `analyses` ve `analysis_items` **tek transaction** içinde yazılır. Ya ikisi birden kaydedilir ya hiçbiri.
- **Geliştirme ortamı:** Tek bir Supabase cloud projesi yeterli (lokal Supabase Docker ister). Not: ücretsiz Supabase projeleri bir süre kullanılmayınca duraklatılır (pause).

---

## 8. Frontend

- React + Vite + TypeScript, `react-router` (4 sayfa: login, yeni analiz, geçmiş, detay). Giriş yapılmamışsa korumalı rotalar login sayfasına yönlendirir.
- **Tipler elle yazılmaz:** `npm run gen:types` → `openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.d.ts`. Backend şeması değiştiğinde frontend derlemesi kırılır ve uyumsuzluk hemen görülür.
- i18n: basit `tr.json`/`en.json` + React context. Seçilen dil `output_language` olarak API'ye gönderilir.
- Yeni analiz sayfasında "CV'niz analiz için Google Gemini'ye gönderilir, CV metni saklanmaz" uyarısı gösterilir.
- Analiz sırasında (5–30 sn) yükleniyor durumu gösterilir ve buton devre dışı bırakılır (çift gönderim engellenir).
- Lokal geliştirme: `vite.config.ts` içinde `/api` isteklerini `http://localhost:8000`'e yönlendiren proxy.

---

## 9. Konfigürasyon (env)

**backend/.env.example**
```
GEMINI_API_KEY=
GEMINI_MODEL=
MATCHER=llm                      # llm | keyword
DATABASE_URL=                    # Supavisor transaction pooler :6543
MIGRATION_DATABASE_URL=          # session pooler :5432 (sadece alembic)
SUPABASE_URL=                    # JWKS için
ALLOWED_ORIGINS=http://localhost:5173
DAILY_ANALYSIS_LIMIT=20
MAX_UPLOAD_BYTES=4000000
MAX_CV_CHARS=20000
MAX_JOB_CHARS=10000
```

**frontend/.env.example**
```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=          # herkese açık olması güvenli çünkü RLS deny-all
VITE_API_BASE_URL=               # prod'da backend Vercel URL'i, lokalde boş (proxy kullanılır)
```

`.env` dosyaları **asla** commit edilmez (`.gitignore`).

---

## 10. Deploy (Vercel)

- **Aynı repodan iki Vercel projesi:** `frontend/` (Vite, statik) ve `backend/` (FastAPI). Root Directory ayarları bu klasörler olur.
- `backend/vercel.json`:
  ```json
  {
    "$schema": "https://openapi.vercel.sh/vercel.json",
    "functions": {
      "app/main.py": {
        "maxDuration": 60,
        "excludeFiles": "{tests/**,alembic/**}"
      }
    }
  }
  ```
- CORS: `ALLOWED_ORIGINS` prod'da frontend domain'ini içerir.
- Supabase Auth: Site URL ve Redirect URL'lere prod frontend domain'i eklenir. Google Cloud OAuth client'ında Supabase callback URL'i tanımlanır.
- Vercel Firewall: `/api/v1/analyses` için IP bazlı rate limit kuralı (günlük kotaya ek bir katman).
- Bağımlılıklar hafif tutulur (`torch`/`sentence-transformers` yok). Vercel fonksiyon paket boyutu sınırlıdır.
- Gemini tarafında kota veya bütçe sınırı ayarlanır.

---

## 11. Uygulama Fazları

Her faz dikey bir dilimdir (vertical slice). Faz sonunda çalışan ve test edilmiş bir şey olur. **Veritabanı ve auth, çekirdek analiz çalıştıktan sonra eklenir.** Böylece bir şey bozulduğunda sorunun hangi katmanda olduğu bilinir ve geliştirme sırasında her istekte login gerekmez.

| Faz | İş | Bitti kriteri |
|---|---|---|
| **0** | **Git kurulumunu kullanıcıya yaptır** (bkz. §12a): proje klasöründe `git init` (bir üst dizindeki repo kullanıcının ev dizini, oraya commit edilmemeli), GitHub'da repo oluşturma, `remote` ekleme, ilk push. Ardından `.gitignore`, `uv` ile backend iskeleti, `config.py`, `/api/health` | `uv run uvicorn app.main:app --reload` → health 200. Kullanıcı ilk commit'i GitHub'a push etmiş |
| **1** | `parsing/` + `/documents/parse` + fixture'lar (TR ve EN, PDF ve DOCX) + testler | Fixture CV'lerin metni doğru okunuyor, hata kodları (413/415/422) test edildi |
| **2** | Tüm Pydantic şemaları, `scoring.py`, `text_normalization.py`, `KeywordMatcher`, `analysis_service`, `POST /analyses` (henüz auth ve DB yok, `id`/`created_at` sahte üretilir) + testler | `MATCHER=keyword` ile uçtan uca skor dönüyor. Scoring ve normalization testleri geçiyor |
| **3** | Frontend: Vite + TS, tip üretimi, proxy, yeni analiz sayfası + sonuç görünümü, i18n | Tarayıcıdan analiz yapılıp sonuç görülüyor |
| **4** | `llm/` + `LLMMatcher` + evidence doğrulaması. LLM client mock'lanarak test edilir | Gerçek TR↔EN ilan/CV çiftleriyle anlamlı sonuç alınıyor |
| **5** | Supabase projesi, SQLAlchemy modelleri, Alembic migration (RLS dahil), `AnalysisRepository` (SQL + InMemory), kaydetme + GET liste/detay + DELETE | Analizler kaydediliyor, geçmiş listeleniyor. API testleri InMemory repo ile geçiyor |
| **6** | Google OAuth (Supabase + Google Cloud), frontend login ve korumalı rotalar, `get_current_user`, tüm endpoint'lerde `user_id` filtresi, günlük kota | Kullanıcı A, kullanıcı B'nin analizini göremiyor (test ile kanıtlanmış) |
| **7** | Vercel deploy (2 proje), CORS, `vercel.json`, Firewall kuralı, gizlilik uyarısı, README (kurulum adımları) | Prod URL'de giriş yapılıp analiz yapılabiliyor |

---

## 12. Kodlama Kuralları

- Python ≥ 3.12, bağımlılık yönetimi `uv` (`pyproject.toml` + `uv.lock`). Lint ve format için `ruff`, testler için `pytest`.
- Route fonksiyonları ince tutulur: girdi doğrulama → servis çağrısı → yanıt. İş mantığı `services/` içinde olur.
- Testler gerçek Gemini'ye veya gerçek veritabanına **bağlanmaz** (mock / KeywordMatcher / InMemory repo kullanılır).
- Gizli anahtarlar yalnızca env değişkenlerinde tutulur. CV içeriği loglanmaz.
- Her faz sonunda: testler geçmeli, junior geliştirici için "bu fazda alınan kararlar ve nedenleri" özeti yazılmalı, ardından §12a'daki git adımları kullanıcıya **tarif edilmeli**.

### 12a. Git ve GitHub: kullanıcı yapar, AI tarif eder

Kullanıcı git ve GitHub'ı öğrenmek istiyor. Bu yüzden:

- **AI hiçbir git/GitHub komutunu kendisi çalıştırmaz.** Bu kural `init`, `add`, `commit`, `branch`, `checkout`/`switch`, `merge`, `push`, `pull`, `remote`, `gh` ve PR açma dahil tüm komutlar için geçerli. Sadece okuma amaçlı `git status`, `git diff` ve `git log` çalıştırabilir.
- Her git adımında AI şunları verir:
  1. **Çalıştırılacak komutlar**, sırasıyla ve kopyalanabilir şekilde.
  2. **Her komutun ne yaptığı**, tek cümleyle ("`git add` değişiklikleri staging area'ya alır, yani bir sonraki commit'e girecekleri seçer").
  3. **Önerilen commit mesajı ve neden böyle yazıldığı.**
  4. **Kontrol yolu:** kullanıcı komutu çalıştırdıktan sonra neye bakmalı (`git status` çıktısında ne görmeli).
- Kullanıcı komutu Claude Code içinde `! <komut>` şeklinde çalıştırabilir. Böylece çıktı konuşmaya düşer ve AI sonucu kontrol edebilir.
- Hata olursa (merge conflict, reddedilen push vb.) AI çözümü yine tarif eder. `reset --hard`, `push --force` gibi geri alınamaz komutları önermeden önce ne kaybedileceğini açıkça söyler.
- Yeni bir kavram ilk kez geçtiğinde (staging area, remote, branch, PR, merge) 2–3 cümlelik bir açıklama eklenir. Sonraki geçişlerde tekrar açıklanmaz.

**İş akışı (GitHub Flow):**
- `main` her zaman çalışır durumda olur. Her faz için ayrı bir branch açılır: `feat/phase-1-parsing`, `feat/phase-2-scoring` vb.
- Faz içinde mantıklı ara noktalarda küçük commit'ler atılır. Faz sonunda GitHub'da PR açılır, kullanıcı PR'ı inceleyip `main`'e merge eder.
- **Neden bu akış?** Gerçek ekiplerdeki çalışma şekli bu. PR ekranı yapılan değişikliğin toplu bir özetini gösterir. Vercel de her PR için otomatik bir preview deploy üretir (Faz 7'den sonra).
- Commit mesajları [Conventional Commits](https://www.conventionalcommits.org/) biçiminde yazılır: `feat: add PDF parser`, `test: add scoring edge cases`, `fix: handle Turkish İ in normalization`, `docs: ...`, `chore: ...`.
- Commit öncesi kontrol: `.env` dosyasının ve `.venv/` klasörünün staging area'da olmadığı `git status` ile doğrulanır.

---

## 13. Sonraya Bırakılanlar (MVP dışı)

1. Eksiklere göre CV iyileştirme önerileri (madde yeniden yazımı)
2. "Geçmişimde en sık eksik çıkan beceriler" istatistik sayfası (`analysis_items` üzerinden SQL)
3. ATS uyumluluk kontrolü
4. Bir CV'yi birden çok ilanla karşılaştırma ve sıralama (burada embedding mantıklı hale gelir)
5. Hesap silme endpoint'i (KVKK: `auth.users` silinince cascade)
6. İlan URL'sinden otomatik metin çekme, OCR, cover letter üretimi, PDF rapor çıktısı
7. Uzun analizler için streaming (SSE) ile ilerleme gösterimi

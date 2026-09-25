import os

# Testler asla gerçek Gemini'ye veya gerçek bir veritabanına bağlanmamalı
# (CLAUDE.md). Geliştiricinin backend/.env dosyasında MATCHER=llm ayarlı olsa
# bile, pydantic-settings OS ortam değişkenlerini .env dosyasından önce
# okuduğu için burada set edilen değerler .env'i ezer ve testleri güvenli
# varsayılanlara sabitler. conftest.py, pytest tarafından bu dizindeki diğer
# test modülleri (ve onların `app.main` import'ları) import edilmeden önce
# otomatik olarak yüklenir.
os.environ["MATCHER"] = "keyword"
os.environ["GEMINI_API_KEY"] = ""
os.environ["DATABASE_URL"] = ""

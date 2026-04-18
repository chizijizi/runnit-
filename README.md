# 🏔️ RUNNIT

Platforma za avanturističke aktivnosti — paintball, kayak, planinarenje, karting, let balonom i više.

## Tech stack

- **Backend:** FastAPI (Python)
- **Baza:** PostgreSQL + SQLAlchemy 2.0
- **Auth:** JWT (python-jose + bcrypt)
- **Migracije:** Alembic
- **Deploy:** Render / Railway

## Lokalni razvoj

### 1. Kloniraj i postavi environment

```bash
cp .env.example .env
# Uredi .env s tvojim PostgreSQL podacima
```

### 2. Instaliraj ovisnosti

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Postavi bazu i pokreni migracije

```bash
bash scripts/init_db.sh
```

### 4. Pokreni server

```bash
uvicorn app.main:app --reload
```

API dokumentacija: http://localhost:8000/docs

## Struktura projekta

```
runnit/
├── app/
│   ├── api/v1/endpoints/   # Rute (auth, activities, bookings...)
│   ├── core/               # Config, security (JWT)
│   ├── db/                 # Session, baza
│   ├── models/             # SQLAlchemy modeli
│   ├── schemas/            # Pydantic sheme
│   ├── services/           # Poslovna logika
│   └── main.py             # FastAPI app
├── migrations/             # Alembic migracije
├── scripts/                # Pomocne skripte
├── tests/                  # Testovi
├── .env.example
├── alembic.ini
├── Procfile                # Za Render/Railway
└── requirements.txt
```

## Deploy na Render

1. Push na GitHub
2. Novi Web Service na render.com → poveži repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Dodaj environment varijable iz `.env.example`
6. Dodaj PostgreSQL bazu (Render nudi besplatnu)

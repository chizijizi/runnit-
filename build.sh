#!/bin/bash
set -e

echo "🔧 Instalacija dependencies..."
pip install -r requirements.txt

echo "🗄️  Pokretanje migracija..."
alembic upgrade head || python -c "
from app.db.session import engine
from app.models.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Tablice kreirane direktno')
"

echo "🌱 Seedanje kategorija..."
python -c "
import sys
sys.path.insert(0, '.')
from app.db.session import SessionLocal, engine
from app.models.models import Base, Category
Base.metadata.create_all(bind=engine)
CATEGORIES = [
    {'name': 'Paintball',      'icon': 'paintball'},
    {'name': 'Kayak',          'icon': 'kayak'},
    {'name': 'Planinarenje',   'icon': 'hiking'},
    {'name': 'Karting',        'icon': 'karting'},
    {'name': 'Let balonom',    'icon': 'balloon'},
    {'name': 'Bungee jumping', 'icon': 'bungee'},
    {'name': 'Zipline',        'icon': 'zipline'},
    {'name': 'Rafting',        'icon': 'rafting'},
]
db = SessionLocal()
added = 0
for cat in CATEGORIES:
    if not db.query(Category).filter(Category.name == cat['name']).first():
        db.add(Category(**cat))
        added += 1
db.commit()
db.close()
print(f'✅ {added} kategorija dodano')
"

echo "✅ Build završen — RUNNIT spreman!"

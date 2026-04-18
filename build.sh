#!/bin/bash
# Pokreće se na Render-u pri svakom deployu PRIJE pokretanja servera
set -e

echo "🔧 Instalacija dependencies..."
pip install -r requirements.txt

echo "🗄️  Pokretanje migracija..."
alembic upgrade head

echo "✅ Build završen — RUNNIT spreman!"

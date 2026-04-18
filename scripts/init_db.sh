#!/bin/bash
# scripts/init_db.sh
# Pokreni jedanput za postavljanje migracija

set -e

echo "🚀 RUNNIT — Inicijalizacija baze podataka"

# Inicijaliziraj alembic (samo ako env/ ne postoji)
if [ ! -d "migrations" ]; then
  alembic init migrations
  echo "✅ Alembic inicijaliziran"
fi

# Kreiraj prvu migraciju
alembic revision --autogenerate -m "initial schema"
echo "✅ Migracija kreirana"

# Primijeni migracije
alembic upgrade head
echo "✅ Baza ažurirana"

echo "🎉 Gotovo! RUNNIT baza je spremna."

"""
scripts/seed.py
Popunjava bazu s kategorijama i demo podacima.
Pokreni: python -m scripts.seed
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.models import Category, Provider, Activity
from app.core.security import hash_password


CATEGORIES = [
    {"name": "Paintball",      "icon": "🎯"},
    {"name": "Kayak",          "icon": "🛶"},
    {"name": "Planinarenje",   "icon": "🏔️"},
    {"name": "Karting",        "icon": "🏎️"},
    {"name": "Let balonom",    "icon": "🎈"},
    {"name": "Bungee jumping", "icon": "🪂"},
    {"name": "Zipline",        "icon": "🌲"},
    {"name": "Rafting",        "icon": "🌊"},
]

def seed():
    db = SessionLocal()
    try:
        # Kategorije
        for cat_data in CATEGORIES:
            if not db.query(Category).filter(Category.name == cat_data["name"]).first():
                db.add(Category(**cat_data))
        db.commit()
        print(f"✅ {len(CATEGORIES)} kategorija dodano")

        # Demo provider
        provider = db.query(Provider).filter(Provider.name == "Adventure Zone Varaždin").first()
        if not provider:
            provider = Provider(
                name="Adventure Zone Varaždin",
                description="Varaždinsko središte avanturističkih aktivnosti",
                address="Varaždin, Hrvatska",
                lat=46.3047,
                lng=16.3368,
                contact_email="info@adventurezone.hr",
                verified=True,
            )
            db.add(provider)
            db.commit()
            db.refresh(provider)
            print("✅ Demo provider dodan")

        # Demo aktivnost
        paintball_cat = db.query(Category).filter(Category.name == "Paintball").first()
        if paintball_cat and not db.query(Activity).filter(Activity.title == "Paintball Varaždin").first():
            db.add(Activity(
                provider_id=provider.id,
                category_id=paintball_cat.id,
                title="Paintball Varaždin",
                description="Adrenalinska paintball bitka za do 20 igrača. Oprema uključena.",
                price=25.0,
                duration_min=90,
                lat=46.3100,
                lng=16.3400,
                active=True,
            ))
            db.commit()
            print("✅ Demo aktivnost dodana")

        print("\n🎉 Seed završen! Pokreni server: uvicorn app.main:app --reload")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

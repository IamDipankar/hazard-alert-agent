"""
Import people from the Pseudo_Human_Database_Hackathon.xlsx spreadsheet into PostgreSQL.

Usage:
    python -m scripts.import_people [--file path/to/xlsx]
"""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.app.database import Base
from backend.app.models.person import Person

import openpyxl


DEFAULT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Pseudo_Human_Database_Hackathon.xlsx")


# Coordinate ranges for Bangladesh districts (rough approximations for demo)
DISTRICT_COORDS = {
    "Cox's Bazar": (21.45, 91.97), "Chittagong": (22.35, 91.83), "Noakhali": (22.87, 91.10),
    "Patuakhali": (22.35, 90.35), "Barguna": (22.15, 90.12), "Bagerhat": (22.66, 89.79),
    "Khulna": (22.82, 89.55), "Satkhira": (22.71, 89.07), "Bhola": (22.69, 90.65),
    "Lakshmipur": (22.95, 90.83), "Feni": (23.02, 91.40), "Chandpur": (23.23, 90.65),
    "Pirojpur": (22.58, 89.97), "Jhalokati": (22.64, 90.20), "Barisal": (22.70, 90.37),
    "Sunamganj": (25.07, 91.40), "Sylhet": (24.90, 91.87), "Netrokona": (24.88, 90.73),
    "Kurigram": (25.81, 89.64), "Jamalpur": (24.94, 89.94), "Sirajganj": (24.45, 89.70),
    "Rangpur": (25.75, 89.25), "Gaibandha": (25.33, 89.53), "Bogra": (24.85, 89.37),
    "Bandarban": (22.20, 92.22), "Rangamati": (22.65, 92.17), "Khagrachhari": (23.10, 91.98),
}

def get_coords(district: str, index: int):
    """Get approximate coordinates for a district with slight randomization."""
    import random
    random.seed(index)
    base = DISTRICT_COORDS.get(district, (23.0 + random.uniform(-2, 2), 90.0 + random.uniform(-1, 1)))
    return base[0] + random.uniform(-0.15, 0.15), base[1] + random.uniform(-0.15, 0.15)


# Column mapping — adjust these based on actual spreadsheet headers
COLUMN_MAP = {
    "name": ["name", "নাম", "Name", "person_name"],
    "phone": ["phone", "ফোন", "Phone", "mobile"],
    "gender": ["gender", "লিঙ্গ", "Gender"],
    "district": ["district", "জেলা", "District"],
    "upazila": ["upazila", "উপজেলা", "Upazila", "sub_district"],
    "union_name": ["union", "ইউনিয়ন", "Union", "union_name"],
    "village": ["village", "গ্রাম", "Village"],
    "housing_type_known": ["housing_type", "house_type", "ঘরের ধরন", "Housing Type", "housing"],
    "livelihood_known": ["livelihood", "জীবিকা", "Livelihood", "occupation"],
    "vulnerable_members_known": ["vulnerable_members", "ঝুঁকিপূর্ণ সদস্য", "Vulnerable Members", "vulnerability"],
    "water_source_known": ["water_source", "পানির উৎস", "Water Source"],
    "latrine_type_known": ["latrine_type", "ল্যাট্রিন", "Latrine Type", "latrine"],
    "income_level": ["income", "আয়", "Income", "income_level"],
    "family_size": ["family_size", "পরিবারের আকার", "Family Size"],
}


def find_column(header_row, field_name):
    """Find column index by matching possible header names."""
    possible = COLUMN_MAP.get(field_name, [field_name])
    for idx, cell in enumerate(header_row):
        val = str(cell.value or "").strip().lower()
        for p in possible:
            if val == p.lower() or p.lower() in val:
                return idx
    return None


def main(filepath: str = DEFAULT_FILE):
    from dotenv import load_dotenv
    load_dotenv()

    db_url = os.getenv("DATABASE_URL_SYNC", "postgresql://postgres:postgres@localhost:5432/hazard_alert")
    engine = create_engine(db_url)

    # Ensure tables exist
    Base.metadata.create_all(engine)

    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows())
    if not rows:
        print("Empty spreadsheet!")
        return

    header_row = rows[0]
    print(f"Headers: {[str(c.value) for c in header_row]}")

    # Find column indices
    col_indices = {}
    for field in COLUMN_MAP:
        idx = find_column(header_row, field)
        if idx is not None:
            col_indices[field] = idx
            print(f"  → {field}: column {idx} ({header_row[idx].value})")
        else:
            print(f"  ⚠ {field}: not found")

    imported = 0
    skipped = 0

    with Session(engine) as session:
        for i, row in enumerate(rows[1:], start=1):
            cells = [c.value for c in row]

            # Get name — required
            name_idx = col_indices.get("name")
            if name_idx is None or not cells[name_idx]:
                skipped += 1
                continue

            name = str(cells[name_idx]).strip()
            district = str(cells[col_indices["district"]]).strip() if "district" in col_indices and cells[col_indices["district"]] else None

            # Generate coordinates
            lat, lng = get_coords(district or "", i)

            person = Person(
                id=uuid.uuid4(),
                external_person_id=f"import_{i}",
                name=name,
                phone=str(cells[col_indices["phone"]]).strip() if "phone" in col_indices and cells[col_indices["phone"]] else None,
                gender=str(cells[col_indices["gender"]]).strip() if "gender" in col_indices and cells[col_indices["gender"]] else None,
                district=district,
                upazila=str(cells[col_indices["upazila"]]).strip() if "upazila" in col_indices and cells[col_indices["upazila"]] else None,
                union_name=str(cells[col_indices["union_name"]]).strip() if "union_name" in col_indices and cells[col_indices["union_name"]] else None,
                village=str(cells[col_indices["village"]]).strip() if "village" in col_indices and cells[col_indices["village"]] else None,
                lat=lat,
                lng=lng,
                housing_type_known=str(cells[col_indices["housing_type_known"]]).strip() if "housing_type_known" in col_indices and cells[col_indices["housing_type_known"]] else None,
                livelihood_known=str(cells[col_indices["livelihood_known"]]).strip() if "livelihood_known" in col_indices and cells[col_indices["livelihood_known"]] else None,
                vulnerable_members_known=str(cells[col_indices["vulnerable_members_known"]]).strip() if "vulnerable_members_known" in col_indices and cells[col_indices["vulnerable_members_known"]] else None,
                water_source_known=str(cells[col_indices["water_source_known"]]).strip() if "water_source_known" in col_indices and cells[col_indices["water_source_known"]] else None,
                latrine_type_known=str(cells[col_indices["latrine_type_known"]]).strip() if "latrine_type_known" in col_indices and cells[col_indices["latrine_type_known"]] else None,
                income_level=str(cells[col_indices["income_level"]]).strip() if "income_level" in col_indices and cells[col_indices["income_level"]] else None,
                family_size=int(cells[col_indices["family_size"]]) if "family_size" in col_indices and cells[col_indices["family_size"]] else None,
            )
            session.add(person)
            imported += 1

        session.commit()

    print(f"\n✅ Imported {imported} people, skipped {skipped}")
    wb.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=DEFAULT_FILE, help="Path to XLSX file")
    args = parser.parse_args()
    main(args.file)

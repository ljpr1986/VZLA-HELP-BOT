import json
import shutil
from datetime import datetime
import sys
import unicodedata

PEOPLE_FILE = "people.json"

def normalize_name(name):
    name = name.lower().strip()
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    return " ".join(name.split())

def load_json(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_name, data):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def backup_people():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"people_backup_{timestamp}.json"
    shutil.copy(PEOPLE_FILE, backup_name)
    print(f"✅ Backup creado: {backup_name}")

def is_duplicate(existing_person, new_person):
    existing_cedula = str(existing_person.get("cedula", "")).strip()
    new_cedula = str(new_person.get("cedula", "")).strip()

    if existing_cedula and new_cedula and existing_cedula == new_cedula:
        return True

    existing_name = normalize_name(existing_person.get("nombre", ""))
    new_name = normalize_name(new_person.get("nombre", ""))

    return existing_name == new_name

def merge_person(existing, new):
    for key, value in new.items():
        if value not in ["", None]:
            if existing.get(key) in ["", None]:
                existing[key] = value

    return existing

def main():
    if len(sys.argv) < 2:
        print("Uso: python import_people.py nueva_lista.json")
        return

    new_file = sys.argv[1]

    people = load_json(PEOPLE_FILE)
    new_people = load_json(new_file)

    backup_people()

    added = 0
    duplicates = 0

    for new_person in new_people:
        found = False

        for existing_person in people:
            if is_duplicate(existing_person, new_person):
                merge_person(existing_person, new_person)
                duplicates += 1
                found = True
                break

        if not found:
            people.append(new_person)
            added += 1

    save_json(PEOPLE_FILE, people)

    print("✅ Importación terminada")
    print(f"➕ Nuevos agregados: {added}")
    print(f"🔁 Duplicados encontrados/actualizados: {duplicates}")
    print(f"📋 Total actual: {len(people)}")

if __name__ == "__main__":
    main()
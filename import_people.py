import json
import shutil
from datetime import datetime
import sys
import unicodedata

PEOPLE_FILE = "people.json"

def normalize_text(text):
    text = str(text or "").lower().strip()
    text = ''.join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(text.split())

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

def same_person(existing, new):
    existing_cedula = normalize_text(existing.get("cedula", ""))
    new_cedula = normalize_text(new.get("cedula", ""))

    if existing_cedula and new_cedula and existing_cedula == new_cedula:
        return True

    existing_name = normalize_text(existing.get("nombre", ""))
    new_name = normalize_text(new.get("nombre", ""))

    return existing_name == new_name

def merge_person(existing, new):
    updated = False

    for key, value in new.items():
        if value not in ["", None]:
            if existing.get(key) in ["", None]:
                existing[key] = value
                updated = True

    return updated

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
    updated = 0

    print("\nProcesando registros...\n")

    for new_person in new_people:
        found = False

        for existing_person in people:
            if same_person(existing_person, new_person):
                was_updated = merge_person(existing_person, new_person)

                print(f"🔁 DUPLICADO: {new_person.get('nombre', '')}")

                duplicates += 1
                if was_updated:
                    updated += 1

                found = True
                break

        if not found:
            people.append(new_person)
            print(f"➕ NUEVO: {new_person.get('nombre', '')}")
            added += 1

    save_json(PEOPLE_FILE, people)

    print("\n✅ Importación terminada")
    print(f"➕ Nuevos agregados: {added}")
    print(f"🔁 Duplicados encontrados: {duplicates}")
    print(f"♻️ Registros actualizados: {updated}")
    print(f"📋 Total actual: {len(people)}")

if __name__ == "__main__":
    main()
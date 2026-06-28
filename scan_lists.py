import os
import json
import shutil
from datetime import datetime
from PIL import Image
import pytesseract

IMAGES_FOLDER = "imports/images"
OUTPUT_FILE = "imports/output/nueva_lista_revisar.json"
BACKUP_FOLDER = "backups"

DEFAULT_LOCATION = "Campo de Golf Caribe"
DEFAULT_STATUS = "Sobreviviente"

def backup_people():
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    if os.path.exists("people.json"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy("people.json", f"{BACKUP_FOLDER}/people_backup_{timestamp}.json")

def clean_line(line):
    line = line.strip()
    line = line.replace(".", "")
    line = line.replace("•", "")
    return " ".join(line.split())

def looks_like_name(line):
    if len(line) < 5:
        return False
    if any(char.isdigit() for char in line):
        return False
    bad_words = ["campo", "golf", "caribe", "sobreviviente", "sobrevivientes", "lista"]
    if line.lower() in bad_words:
        return False
    return True

def person_from_line(line, source):
    menor = "menor" in line.lower()
    name = line.replace("(menor)", "").replace("menor", "").strip()

    return {
        "nombre": name,
        "cedula": "",
        "edad": None,
        "sexo": "",
        "ubicacion": DEFAULT_LOCATION,
        "origen": "",
        "estado": DEFAULT_STATUS,
        "verificado": False,
        "fuente": source,
        "observacion": "Menor" if menor else ""
    }

def main():
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    os.makedirs("imports/output", exist_ok=True)

    all_people = []

    for filename in os.listdir(IMAGES_FOLDER):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        path = os.path.join(IMAGES_FOLDER, filename)
        print(f"Procesando: {filename}")

        image = Image.open(path)
        text = pytesseract.image_to_string(image, lang="eng")

        for line in text.splitlines():
            line = clean_line(line)
            if looks_like_name(line):
                all_people.append(person_from_line(line, filename))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_people, f, ensure_ascii=False, indent=2)

    print("")
    print("✅ Escaneo terminado")
    print(f"Personas detectadas: {len(all_people)}")
    print(f"Archivo creado: {OUTPUT_FILE}")
    print("")
    print("IMPORTANTE: Revisa el archivo antes de importarlo.")

if __name__ == "__main__":
    main()
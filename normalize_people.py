import json
import re
from collections import Counter

PEOPLE_FILE = "people.json"

def clean_text(text):
    text = str(text or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text

def normalize_hospital(name):
    raw = clean_text(name)
    upper = raw.upper()

    if "DOMINGO LUCIANI" in upper or "LLANITO" in upper:
        return "Hospital Domingo Luciani"

    if "PEREZ" in upper or "PÉREZ" in upper or "CARRE" in upper:
        return "Hospital Pérez Carreño"

    if "VARGAS" in upper and "GUAIRA" not in upper:
        return "Hospital Vargas de Caracas"

    if "JOSE MARIA VARGAS" in upper or "VARGAS LA GUAIRA" in upper:
        return "Hospital Dr. José María Vargas La Guaira"

    if "JM DE LOS RIOS" in upper or "J M DE LOS RIOS" in upper or "LOS RIOS" in upper or "NIÑOS" in upper:
        return "Hospital JM de los Ríos"

    if "UNIVERSITARIO" in upper:
        return "Hospital Universitario de Caracas"

    if "CATIA" in upper or "RICARDO BAQUERO" in upper or "BAQUERO" in upper:
        return "Hospital Dr. Ricardo Baquero González"

    if "CIUDAD CARIBIA" in upper:
        return "Hospital Ciudad Caribia"

    if "VICTORINO SANTAELLA" in upper:
        return "Hospital Victorino Santaella"

    if "CLINICA EL AVILA" in upper or "CLÍNICA EL ÁVILA" in upper:
        return "Clínica El Ávila"

    if "CAMPO DE GOLF" in upper or "PLAYA LOS COCOS" in upper:
        return "Refugiados Campo de Golf Playa Los Cocos"

    return raw.title()

with open(PEOPLE_FILE, "r", encoding="utf-8") as f:
    people = json.load(f)

changed = 0

for p in people:
    old = p.get("ubicacion", "")
    new = normalize_hospital(old)

    if old != new:
        p["ubicacion_original"] = old
        p["ubicacion"] = new
        changed += 1

with open(PEOPLE_FILE, "w", encoding="utf-8") as f:
    json.dump(people, f, ensure_ascii=False, indent=4)

counts = Counter(p.get("ubicacion", "") for p in people if p.get("ubicacion", ""))

print("Personas:", len(people))
print("Ubicaciones normalizadas:", changed)
print("Hospitales/ubicaciones únicos:", len(counts))
print("\nTop ubicaciones:")
for name, total in counts.most_common(20):
    print(f"- {name}: {total}")
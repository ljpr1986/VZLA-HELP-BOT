import json
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Obtener el token desde una variable de entorno
TOKEN = os.getenv("BOT_TOKEN")

# Si no existe la variable, mostrar un error claro
if not TOKEN:
    raise ValueError(
        "BOT_TOKEN no está configurado.\n"
        "En tu PC ejecuta:\n"
        "set BOT_TOKEN=TU_TOKEN\n\n"
        "En Railway crea la variable BOT_TOKEN con el token de BotFather."
    )

PEOPLE_FILE = "people.json"


def load_people():
    with open(PEOPLE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_people(data):
    with open(PEOPLE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def is_duplicate(new_person, people):
    new_cedula = str(new_person.get("cedula", "")).strip()
    new_nombre = new_person.get("nombre", "").strip().lower()
    new_ubicacion = new_person.get("ubicacion", "").strip().lower()

    for person in people:
        cedula = str(person.get("cedula", "")).strip()
        nombre = person.get("nombre", "").strip().lower()
        ubicacion = person.get("ubicacion", "").strip().lower()

        if new_cedula and cedula == new_cedula:
            return True

        if new_nombre and new_ubicacion and nombre == new_nombre and ubicacion == new_ubicacion:
            return True

    return False


main_menu = ReplyKeyboardMarkup(
    [
        ["🔍 Buscar familiar"],
        ["➕ Agregar información"],
        ["🏥 Ver hospitales"],
        ["ℹ️ Ayuda"]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇻🇪 Bot de ayuda para ubicar personas\n\n"
        "Puedes buscar familiares por nombre o cédula, o agregar información de personas ubicadas en hospitales.\n\n"
        "Selecciona una opción:",
        reply_markup=main_menu
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Opciones disponibles:\n\n"
        "🔍 Buscar familiar: busca por nombre o cédula.\n"
        "➕ Agregar información: registra datos de una persona.\n"
        "🏥 Ver hospitales: muestra centros hospitalarios registrados."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "Buscar familiar" in text:
        context.user_data["mode"] = "search"
        await update.message.reply_text("Escribe el nombre, apellido o cédula de la persona que buscas:")
        return

    if "Agregar" in text:
        context.user_data["mode"] = "add_nombre"
        context.user_data["new_person"] = {}
        await update.message.reply_text("Nombre completo de la persona:")
        return

    if "Ver hospitales" in text:
        people = load_people()
        hospitales = sorted(set(p.get("ubicacion", "") for p in people if p.get("ubicacion", "")))

        if not hospitales:
            await update.message.reply_text("No hay hospitales registrados todavía.")
            return

        response = "🏥 Hospitales registrados:\n\n"

        for hospital in hospitales:
            total = sum(1 for p in people if p.get("ubicacion", "") == hospital)
            line = f"- {hospital} ({total} personas)\n"

            if len(response) + len(line) > 3500:
                await update.message.reply_text(response)
                response = ""

            response += line

        if response.strip():
            await update.message.reply_text(response)

        return

    if "Ayuda" in text:
        await help_command(update, context)
        return

    mode = context.user_data.get("mode")

    if mode == "search":
        people = load_people()
        query = text.lower()

        results = []
        for person in people:
            nombre = person.get("nombre", "").lower()
            cedula = str(person.get("cedula", "")).lower()
            ubicacion = person.get("ubicacion", "").lower()
            origen = person.get("origen", "").lower()

            if query in nombre or query in cedula or query in ubicacion or query in origen:
                results.append(person)

        if not results:
            await update.message.reply_text("No encontré resultados con esa información.")
        else:
            response = "🔎 Resultados encontrados:\n\n"

            for p in results[:10]:
                verificado = "✅ Sí" if p.get("verificado") else "❌ No"

                response += (
                    f"👤 Nombre: {p.get('nombre', 'No disponible')}\n"
                    f"🪪 Cédula: {p.get('cedula', 'No disponible')}\n"
                    f"🎂 Edad: {p.get('edad', 'No disponible')}\n"
                    f"🚻 Sexo: {p.get('sexo', 'No disponible')}\n"
                    f"📌 Estado: {p.get('estado', 'No disponible')}\n"
                    f"🏥 Ubicación: {p.get('ubicacion', 'No disponible')}\n"
                    f"📍 Origen: {p.get('origen', 'No disponible')}\n"
                    f"🔒 Verificado: {verificado}\n\n"
                )

            await update.message.reply_text(response)

        context.user_data["mode"] = None
        return

    if mode == "add_nombre":
        context.user_data["new_person"]["nombre"] = text
        context.user_data["mode"] = "add_cedula"
        await update.message.reply_text("Cédula de la persona. Si no la sabes, escribe: No sé")
        return

    if mode == "add_cedula":
        context.user_data["new_person"]["cedula"] = "" if text.lower() == "no sé" else text
        context.user_data["mode"] = "add_edad"
        await update.message.reply_text("Edad de la persona. Si no la sabes, escribe: No sé")
        return

    if mode == "add_edad":
        if text.lower() == "no sé":
            context.user_data["new_person"]["edad"] = None
        else:
            try:
                context.user_data["new_person"]["edad"] = int(text)
            except ValueError:
                context.user_data["new_person"]["edad"] = None

        context.user_data["mode"] = "add_sexo"
        await update.message.reply_text("Sexo de la persona: M, F o No sé")
        return

    if mode == "add_sexo":
        context.user_data["new_person"]["sexo"] = "" if text.lower() == "no sé" else text.upper()
        context.user_data["mode"] = "add_ubicacion"
        await update.message.reply_text("Hospital, centro o ubicación donde fue vista:")
        return

    if mode == "add_ubicacion":
        context.user_data["new_person"]["ubicacion"] = text
        context.user_data["mode"] = "add_origen"
        await update.message.reply_text("Origen, ciudad o sector. Si no lo sabes, escribe: No sé")
        return

    if mode == "add_origen":
        context.user_data["new_person"]["origen"] = "" if text.lower() == "no sé" else text
        context.user_data["mode"] = "add_estado"
        await update.message.reply_text("Estado de la persona: Hospitalizado, Ubicado, Desaparecido, Trasladado o Fallecido")
        return

    if mode == "add_estado":
        new_person = context.user_data["new_person"]
        new_person["estado"] = text
        new_person["verificado"] = False
        new_person["fecha_registro"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_person["telegram_user"] = update.effective_user.username or ""
        new_person["telegram_id"] = update.effective_user.id

        people = load_people()

        if is_duplicate(new_person, people):
            await update.message.reply_text(
                "⚠️ Esta persona parece que ya está registrada.\n\n"
                "No agregué un duplicado.",
                reply_markup=main_menu
            )
        else:
            people.append(new_person)
            save_people(people)

            await update.message.reply_text(
                "✅ Información agregada correctamente.\n\n"
                "Gracias por ayudar. Esta información podrá ser encontrada por otras personas.",
                reply_markup=main_menu
            )

        context.user_data["mode"] = None
        context.user_data["new_person"] = {}
        return

    await update.message.reply_text("Selecciona una opción del menú.", reply_markup=main_menu)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()

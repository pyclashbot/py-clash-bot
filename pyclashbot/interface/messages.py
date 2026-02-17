"""
Translation messages for Py-Clash-Bot.
This file contains the dictionary mappings for supported languages.
PRO TIP for Contributors:
- To add a new language, create a new dictionary (e.g. FR_TRANSLATIONS) and add it to the 'translations' map in i18n.py (or logic).
- Keys are the original English strings found in the UI.
"""

ES_TRANSLATIONS = {
    # Main UI
    "py-clash-bot": "py-clash-bot (Español)",
    "Start": "Iniciar",
    "Stop": "Detener",
    "Force Stop": "Forzar Detención",
    "Retry": "Reintentar",
    "Jobs": "Misiones",
    "Emulator": "Emulador",
    "Stats": "Estadísticas",
    "Misc": "Varios",
    "Appearance": "Apariencia",
    "Select Theme:": "Seleccionar Tema:",
    "Data Settings": "Configuración de Datos",
    "Display Settings": "Configuración de Pantalla",
    "Open Logs Folder": "Abrir Carpeta de Registros",
    # "Discord Rich Presence": "Presencia Rica en Discord", # Requested to leave as is
    
    # Jobs
    "⚔️ Classic 1v1 battles": "⚔️ Batallas Clásicas 1v1",
    "👥 Classic 2v2 battles": "👥 Batallas Clásicas 2v2",
    "🏆 Trophy Road battles": "🏆 Camino de Trofeos",
    "🎲 Randomize Deck": "🎲 Mazo Aleatorio",
    "♻️ Cycle decks": "♻️ Ciclar Mazos",
    "❔ Random plays": "❔ Jugadas Aleatorias",
    "⏭️ Skip win/loss check": "⏭️ Omitir chequeo win/loss",
    "🎯 Card Masteries": "🎯 Maestrías de Cartas",
    "⬆️ Upgrade Cards": "⬆️ Mejorar Cartas",
    "Deck Number to use for Randomization": "Número de Mazo para Aleatorizar",
    "Number of decks to cycle through": "Número de mazos a ciclar",
    
    # Emulator
    "Select Emulator:": "Seleccionar Emulador:",
    "Show advanced settings": "Mostrar configuración avanzada",
    "Google Play Options": "Opciones de Google Play",
    "Render Mode": "Modo de Renderizado",
    "backend": "Motor (backend)",
    "angle": "Ángulo (angle)",
    "egl": "EGL",
    "gles": "GLES",
    "surfaceless": "Sin Superficie (surfaceless)",
    "vulkan": "Vulkan",
    "wsi": "WSI",
    "Device Settings": "Configuración del Dispositivo",
    "Device Serial:": "Serial del Dispositivo:",
    "Connect": "Conectar",
    "Refresh": "Refrescar",
    "Restart ADB": "Reiniciar ADB",
    "Set Size & Density": "Fijar Tamaño y Densidad",
    "Reset Size & Density": "Restablecer Tamaño y Densidad",
    "Sets screen to 419x633 and density to 160": "Ajusta pantalla a 419x633 y densidad a 160",
    "Resets screen size and density to device defaults": "Restablece tamaño y densidad a val. de fábrica",
    
    # Stats
    "Win Rate": "Tasa de Victoria",
    "Battle Stats": "Estadísticas de Batalla",
    "Collection Stats": "Estadísticas de Colección",
    "Bot Stats": "Estadísticas del Bot",
    "Current Streak:": "Racha Actual:",
    "Best Streak:": "Mejor Racha:",
    
    # Stat Labels (Enums)
    "Win": "Victoria",
    "Loss": "Derrota",
    "Moves": "Movimientos",
    "Classic 1v1s": "Clásicas 1v1",
    "Classic 2v2s": "Clásicas 2v2",
    "Trophy Road 1v1s": "Camino de Trofeos 1v1",
    "Decks Randomized": "Mazos Aleatorizados",
    "Decks Cycled": "Mazos Ciclados",
    "Masteries": "Maestrías",
    "Upgrades": "Mejoras",
    "War Chests": "Cofres de Guerra",
    "Bot Failures": "Fallos del Bot",
    "Runtime": "Tiempo de Ejecución",
    "Idle": "Inactivo",
    "Stopping": "Deteniendo",
    "Starting the bot!": "¡Iniciando el bot!",
    "Force stopping bot...": "Forzando detención del bot...",
    "Start cancelled: ADB device '{}' not connected.": "Inicio cancelado: Dispositivo ADB '{}' no conectado.",
    "Please select a device serial first.": "Por favor selecciona un serial de dispositivo primero.",
    "Refreshing ADB devices list...": "Refrescando lista de dispositivos ADB...",
    "No ADB devices found.": "No se encontraron dispositivos ADB.",

    # Messages
    "Critical Error!": "¡Error Crítico!",
    "You must select at least one job!": "¡Debes seleccionar al menos una misión!",
    "No jobs are selected!": "¡No hay misiones seleccionadas!",
    "Restart Required": "Reinicio Requerido",
    "Please restart the application for language changes to take effect.": "Por favor reinicia la aplicación para que el cambio de idioma surta efecto.",
    "Please restart the application for language changes to take effect.\nRestart now?": "Por favor reinicia la aplicación para que el cambio de idioma surta efecto.\n¿Reiniciar ahora?",
    "Clash Royale Not Setup!": "¡Clash Royale No Configurado!",
    "Clash Royale is not installed or setup.\nPlease install Clash Royale, finish the in-game tutorial,\nand log in before using this bot.": "Clash Royale no está instalado o configurado.\nPor favor instala Clash Royale, termina el tutorial del juego,\ne inicia sesión antes de usar este bot.",
    
    # Config/Misc
    "Language": "Idioma",
    "English": "Inglés",
    "Spanish": "Español",
}

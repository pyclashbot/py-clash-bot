import logging

# Global language setting
LANGUAGE = "en"

# Spanish Translations
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
    "Discord Rich Presence": "Presencia Rica en Discord",
    
    # Jobs
    "⚔️ Classic 1v1 battles": "⚔️ Batallas Clásicas 1v1",
    "👥 Classic 2v2 battles": "👥 Batallas Clásicas 2v2",
    "🏆 Trophy Road battles": "🏆 Camino de Trofeos",
    "🎲 Randomize Deck": "🎲 Mazo Aleatorio",
    "♻️ Cycle decks": "♻️ Ciclar Mazos",
    "❔ Random plays": "❔ Jugadas Aleatorias",
    "⏭️ Skip win/loss check": "⏭️ Omitir chequeo ganar/perder",
    "🎯 Card Masteries": "🎯 Maestrías de Cartas",
    "⬆️ Upgrade Cards": "⬆️ Mejorar Cartas",
    "Deck Number to use for Randomization": "Número de Mazo para Aleatorizar",
    "Number of decks to cycle through": "Número de mazos a ciclar",
    
    # Emulator
    "Select Emulator:": "Seleccionar Emulador:",
    "Show advanced settings": "Mostrar configuración avanzada",
    "Google Play Options": "Opciones de Google Play",
    "Render Mode": "Modo de Renderizado",
    "Device Settings": "Configuración del Dispositivo",
    "Device Serial:": "Serial del Dispositivo:",
    "Connect": "Conectar",
    "Refresh": "Refrescar",
    "Restart ADB": "Reiniciar ADB",
    "Set Size & Density": "Fijar Tamaño y Densidad",
    "Reset Size & Density": "Restablecer Tamaño y Densidad",
    
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

    # Messages
    "Critical Error!": "¡Error Crítico!",
    "You must select at least one job!": "¡Debes seleccionar al menos una misión!",
    "Restart Required": "Reinicio Requerido",
    "Please restart the application for language changes to take effect.": "Por favor reinicia la aplicación para que el cambio de idioma surta efecto.",
    "Clash Royale Not Setup!": "¡Clash Royale No Configurado!",
    "Clash Royale is not installed or setup.\nPlease install Clash Royale, finish the in-game tutorial,\nand log in before using this bot.": "Clash Royale no está instalado o configurado.\nPor favor instala Clash Royale, termina el tutorial del juego,\ne inicia sesión antes de usar este bot.",
    
    # Config/Misc
    "Language": "Idioma",
    "English": "Inglés",
    "Spanish": "Español",
}


def set_language(lang: str) -> None:
    """Set the global language."""
    global LANGUAGE
    LANGUAGE = lang

def tr(text: str) -> str:
    """Translate text based on the current global language."""
    if LANGUAGE == "es":
        return ES_TRANSLATIONS.get(text, text)
    return text

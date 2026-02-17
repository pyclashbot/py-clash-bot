import logging
import os
from pyclashbot.interface.messages import ES_TRANSLATIONS

# Global language setting
LANGUAGE = "en"

# Logger for missing translations
# This helps developers find strings that need translation after an update.
MISSING_TRANSLATIONS_FILE = "missing_translations.txt"
_logged_missing_keys = set()

def set_language(lang: str) -> None:
    """Set the global language."""
    global LANGUAGE
    LANGUAGE = lang

def tr(text: str) -> str:
    """Translate text based on the current global language.
    
    If the translation is missing and we are not in English mode,
    it logs the missing key to help with updates.
    """
    if LANGUAGE == "es":
        translation = ES_TRANSLATIONS.get(text)
        if translation is not None:
            return translation
        
        # Fallback and Log
        _log_missing_key(text)
        return text
        
    return text

def _log_missing_key(key: str) -> None:
    """Log missing translation key to a file (only once per session)."""
    if key in _logged_missing_keys:
        return
    
    _logged_missing_keys.add(key)
    
    # You might want to enable this only in dev environments
    # For now, we write it so the user can see what's missing if they are helping.
    try:
        with open(MISSING_TRANSLATIONS_FILE, "a", encoding="utf-8") as f:
            f.write(f'"{key}": "",\n')
    except Exception:
        pass # Fail silently (e.g. permission issues)

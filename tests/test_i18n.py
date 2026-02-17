import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies that might be missing in this environment
sys.modules["ttkbootstrap"] = MagicMock()
sys.modules["ttkbootstrap.constants"] = MagicMock()
sys.modules["ttkbootstrap.tooltip"] = MagicMock()
sys.modules["tkinter"] = MagicMock()
sys.modules["tkinter.messagebox"] = MagicMock()
sys.modules["cv2"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["desktopmagic"] = MagicMock()
sys.modules["pymemuc"] = MagicMock()

class TestI18n(unittest.TestCase):
    def setUp(self):
        # We need to import i18n safely.
        # Since we mocked the deps, we can try importing normally.
        try:
            from pyclashbot.interface import i18n
        except ImportError:
            import importlib.util
            spec = importlib.util.spec_from_file_location("i18n", 
                os.path.join(os.path.dirname(__file__), '../pyclashbot/interface/i18n.py'))
            i18n = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(i18n)
            
        self.i18n = i18n
        self.i18n.set_language("en") # Reset to default

    def test_default_language(self):
        self.assertEqual(self.i18n.LANGUAGE, "en")
        self.assertEqual(self.i18n.tr("Start"), "Start")

    def test_spanish_translation(self):
        self.i18n.set_language("es")
        self.assertEqual(self.i18n.LANGUAGE, "es")
        # Check actual dictionary values
        self.assertEqual(self.i18n.tr("Start"), "Iniciar")
        self.assertEqual(self.i18n.tr("Jobs"), "Misiones")

    def test_fallback_behavior(self):
        self.i18n.set_language("es")
        # "NonExistentString" should return itself
        self.assertEqual(self.i18n.tr("NonExistentString"), "NonExistentString")

    def test_switch_back_to_english(self):
        self.i18n.set_language("es")
        self.i18n.set_language("en")
        self.assertEqual(self.i18n.tr("Start"), "Start")

if __name__ == '__main__':
    unittest.main()

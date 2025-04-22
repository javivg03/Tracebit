import unittest
from scraping.instagram.perfil import scrapear_perfil_instagram_playwright

class TestInstagramPerfil(unittest.TestCase):

    def test_scraper_valido(self):
        """Test con perfil válido"""
        username = "illojuan"
        datos = scrapear_perfil_instagram_playwright(username, max_intentos=1)

        self.assertIsInstance(datos, dict)
        self.assertEqual(datos.get("usuario"), username)
        self.assertIn("nombre", datos)
        self.assertIn("origen", datos)
        print(f"\n✅ Perfil válido test OK → {username}")

    def test_scraper_inexistente(self):
        """Test con perfil inexistente"""
        username = "perfilinexistente123456"
        datos = scrapear_perfil_instagram_playwright(username, max_intentos=1)

        self.assertTrue(datos is None or datos.get("origen") == "error")
        print(f"\n✅ Perfil inexistente manejado → {username}")

if __name__ == "__main__":
    unittest.main()

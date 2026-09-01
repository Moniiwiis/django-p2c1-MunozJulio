from django.test import TestCase
from django.urls import reverse

from .services import cargar_dispositivos


class CatalogoTests(TestCase):
    def test_cargar_dispositivos_incluye_estado(self):
        dispositivos = cargar_dispositivos()

        self.assertTrue(dispositivos)
        self.assertIn("estado", dispositivos[0])

    def test_catalogo_renders_summary(self):
        response = self.client.get(reverse("dispositivos:catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total de Dispositivos")
        self.assertContains(response, "Dispositivos Activos")

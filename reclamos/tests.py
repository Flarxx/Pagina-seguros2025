from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Reclamo, HistorialEstado
from polizas.models import Poliza
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

class ReclamosTestCase(TestCase):

    def setUp(self):
        # Crear usuario cliente y staff
        self.cliente = User.objects.create_user(username='cliente1', password='pass1234')
        self.staff = User.objects.create_user(username='staff1', password='pass1234', is_staff=True)
        
        # Crear póliza para el reclamo
        self.poliza = Poliza.objects.create(poliza_numero='P-001', tipo='AUTO')

        # Cliente logueado
        self.client_cliente = Client()
        self.client_cliente.login(username='cliente1', password='pass1234')

        # Staff logueado
        self.client_staff = Client()
        self.client_staff.login(username='staff1', password='pass1234')

    def test_crear_reclamo(self):
        """El cliente puede crear un reclamo"""
        url = reverse('reclamos:crear')
        data = {
            'poliza': self.poliza.id,
            'motivo': 'Prueba',
            'descripcion': 'Descripción del reclamo',
            'prioridad': 'MEDIA'
        }
        response = self.client_cliente.post(url, data)
        self.assertEqual(response.status_code, 302)  # redirige al detalle
        self.assertEqual(Reclamo.objects.count(), 1)
        reclamo = Reclamo.objects.first()
        self.assertEqual(reclamo.cliente, self.cliente)
        self.assertEqual(reclamo.estado, 'PENDIENTE')

    def test_editar_reclamo_cliente(self):
        """Cliente puede editar reclamo si está en PENDIENTE"""
        reclamo = Reclamo.objects.create(
            poliza=self.poliza,
            cliente=self.cliente,
            motivo='Inicial',
            descripcion='Inicial',
            prioridad='MEDIA'
        )
        url = reverse('reclamos:editar', args=[reclamo.pk])
        data = {'motivo': 'Editado', 'descripcion': 'Editado', 'prioridad': 'ALTA'}
        response = self.client_cliente.post(url, data)
        self.assertEqual(response.status_code, 302)
        reclamo.refresh_from_db()
        self.assertEqual(reclamo.motivo, 'Editado')
        self.assertEqual(reclamo.prioridad, 'ALTA')

    def test_subir_evidencia(self):
        """Cliente puede subir evidencia para su reclamo"""
        reclamo = Reclamo.objects.create(
            poliza=self.poliza,
            cliente=self.cliente,
            motivo='Motivo',
            descripcion='Desc'
        )
        url = reverse('reclamos:subir_evidencia', args=[reclamo.pk])
        # archivo simulado
        archivo = SimpleUploadedFile("archivo.txt", b"contenido prueba")
        response = self.client_cliente.post(url, {'evidencia': archivo})
        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertTrue(resp_json['ok'])
        reclamo.refresh_from_db()
        self.assertTrue(reclamo.evidencia.name.endswith("archivo.txt"))

    def test_cambiar_estado_staff(self):
        """Staff puede cambiar el estado de un reclamo"""
        reclamo = Reclamo.objects.create(
            poliza=self.poliza,
            cliente=self.cliente,
            motivo='Motivo',
            descripcion='Desc'
        )
        url = reverse('reclamos:cambiar_estado', args=[reclamo.pk])
        data = {'nuevo_estado': 'APROBADO', 'nota': 'Todo bien'}
        response = self.client_staff.post(url, data)
        self.assertEqual(response.status_code, 302)
        reclamo.refresh_from_db()
        self.assertEqual(reclamo.estado, 'APROBADO')
        historial = HistorialEstado.objects.filter(reclamo=reclamo).first()
        self.assertIsNotNone(historial)
        self.assertEqual(historial.nota, 'Todo bien')

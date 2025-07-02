from django.test import TestCase, Client
from .models import Room, Room_type


class RoomFilterTestCase(TestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = Client()

        # Crear tipo de habitación
        self.room_type = Room_type.objects.create(
            name="Standard",
            price=100.0,
            max_guests=2
        )

        # Crear habitaciones de prueba
        self.room_1_1 = Room.objects.create(
            name="Room 1.1",
            room_type=self.room_type,
            description="Habitación 1.1"
        )

        self.room_1_2 = Room.objects.create(
            name="Room 1.2",
            room_type=self.room_type,
            description="Habitación 1.2"
        )

        self.room_2_1 = Room.objects.create(
            name="Room 2.1",
            room_type=self.room_type,
            description="Habitación 2.1"
        )

        self.room_10_1 = Room.objects.create(
            name="Room 10.1",
            room_type=self.room_type,
            description="Habitación 10.1"
        )

    def test_filter_successful_room_1(self):
        """Test de filtrado exitoso: Verificar que 'Room 1' encuentra 'Room 1.1', 'Room 1.2'"""
        # Simular la lógica de la vista directamente
        filter_name = '1'
        rooms = Room.objects.filter(name__icontains=filter_name + ".").values("name", "room_type__name", "id")

        room_names = [room['name'] for room in rooms]

        self.assertIn('Room 1.1', room_names)
        self.assertIn('Room 1.2', room_names)
        self.assertEqual(len(room_names), 2)

    def test_filter_precise_room_1_excludes_room_2_1(self):
        """Test de filtrado preciso: Verificar que 'Room 1' NO encuentra 'Room 2.1'"""
        # Simular la lógica de la vista directamente
        filter_name = '1'
        rooms = Room.objects.filter(name__icontains=filter_name + ".").values("name", "room_type__name", "id")

        room_names = [room['name'] for room in rooms]

        self.assertNotIn('Room 2.1', room_names)
        self.assertNotIn('Room 10.1', room_names)

    def test_filter_empty_string(self):
        """Test de filtro vacío: Verificar el comportamiento con cadena vacía"""
        # Simular la lógica de la vista directamente
        filter_name = ''
        if filter_name:
            rooms = Room.objects.filter(name__icontains=filter_name + ".").values("name", "room_type__name", "id")
        else:
            rooms = Room.objects.all().values("name", "room_type__name", "id")

        room_names = [room['name'] for room in rooms]

        # Con filtro vacío debe mostrar todas las habitaciones
        self.assertIn('Room 1.1', room_names)
        self.assertIn('Room 1.2', room_names)
        self.assertIn('Room 2.1', room_names)
        self.assertIn('Room 10.1', room_names)
        self.assertEqual(len(room_names), 4)

    def test_filter_no_results(self):
        """Test de filtro sin resultados: Verificar cuando no hay coincidencias"""
        # Simular la lógica de la vista directamente
        filter_name = 'Room 999'
        rooms = Room.objects.filter(name__icontains=filter_name + ".").values("name", "room_type__name", "id")

        # Verificar que no hay habitaciones
        self.assertEqual(len(rooms), 0)

    def test_filter_logic_room_10_vs_room_1(self):
        """Test adicional: Verificar que 'Room 10' no coincide con 'Room 1.x'"""
        # Simular la lógica de la vista directamente
        filter_name = 'Room 10'
        rooms = Room.objects.filter(name__icontains=filter_name + ".").values("name", "room_type__name", "id")

        room_names = [room['name'] for room in rooms]

        # Debe encontrar Room 10.1 pero no Room 1.1 o Room 1.2
        self.assertIn('Room 10.1', room_names)
        self.assertNotIn('Room 1.1', room_names)
        self.assertNotIn('Room 1.2', room_names)
        self.assertNotIn('Room 2.1', room_names)
        self.assertEqual(len(room_names), 1)

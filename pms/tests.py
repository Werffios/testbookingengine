"""
Para ejecutar los tests:
- Ejecutar todos los tests: python manage.py test pms
- Ejecutar tests específicos: python manage.py test pms.tests.NombreDeLaClase
- Ejecutar un test específico: python manage.py test pms.tests.NombreDeLaClase.nombre_del_test
"""

from django.test import TestCase, Client
from .models import Room, Room_type, Booking, Customer
from datetime import date, timedelta


class A_RoomFilterTestCase(TestCase):
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
        print("Test de filtrado usando '1' | [Room 1.1, Room 1.2]:", room_names)

    def test_filter_precise_room_1_excludes_room_2_1(self):
        """Test de filtrado preciso: Verificar que 'Room 1' NO encuentra 'Room 2.1'"""
        # Simular la lógica de la vista directamente
        filter_name = '1'
        rooms = Room.objects.filter(name__icontains=filter_name + ".").values("name", "room_type__name", "id")

        room_names = [room['name'] for room in rooms]

        self.assertNotIn('Room 2.1', room_names)
        self.assertNotIn('Room 10.1', room_names)
        print("Test de filtrado preciso usando '1' | not [Room 2.1, Room 10.1]:", room_names)

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
        print("Test de filtro vacío | [Room 1.1, Room 1.2, Room 2.1, Room 10.1]:", room_names)

    def test_filter_no_results(self):
        """Test de filtro sin resultados: Verificar cuando no hay coincidencias"""
        # Simular la lógica de la vista directamente
        filter_name = 'Room 999'
        rooms = Room.objects.filter(name__icontains=filter_name + ".").values("name", "room_type__name", "id")

        # Verificar que no hay habitaciones
        self.assertEqual(len(rooms), 0)
        print("Test de filtro sin resultados | []:", list(rooms))

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
        print("Test de filtro | [Room 10.1]:", room_names)


class B_OccupancyTestCase(TestCase):
    def setUp(self):
        """Configurar datos de prueba para el porcentaje de ocupación"""
        # Crear tipo de habitación
        self.room_type = Room_type.objects.create(
            name="Doble",
            price=30.0,
            max_guests=2
        )

        # Crear habitaciones de prueba
        self.room1 = Room.objects.create(
            name="Room 1.1",
            room_type=self.room_type,
            description="Habitación estándar"
        )

        self.room2 = Room.objects.create(
            name="Room 1.2",
            room_type=self.room_type,
            description="Habitación estándar"
        )

        self.room3 = Room.objects.create(
            name="Room 1.3",
            room_type=self.room_type,
            description="Habitación estándar"
        )

        # Crear cliente de prueba (yo)
        self.customer = Customer.objects.create(
            name="Nicolas Suarez",
            email="nasuarezro@unal.edu.co",
            phone="3228192983"
        )

    def calculate_occupancy_percentage(self):
        """Método auxiliar para calcular el porcentaje de ocupación como en la vista"""
        today = date.today()

        # Contar reservas confirmadas (estado = 'NEW' se considera confirmado)
        confirmed_bookings_count = (Booking.objects
                                   .filter(state="NEW")
                                   .filter(checkin__lte=today, checkout__gt=today)
                                   .count())

        # Contar el total de habitaciones
        total_rooms_count = Room.objects.count()

        # Calcular el porcentaje de ocupación
        if total_rooms_count > 0:
            occupancy_percentage = (confirmed_bookings_count / total_rooms_count) * 100
        else:
            occupancy_percentage = 0

        return round(occupancy_percentage, 1)

    def test_occupancy_percentage_zero_bookings(self):
        """Test con 0 reservas confirmadas - debe ser 0%"""
        percentage = self.calculate_occupancy_percentage()
        self.assertEqual(percentage, 0.0)
        print("Test de ocupación con 0 reservas confirmadas: 0.0%", percentage)

    def test_occupancy_percentage_partial_booking(self):
        """Test con reservas parciales - debe calcular porcentaje correcto"""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Crear una reserva confirmada (estado NEW) que incluye hoy
        Booking.objects.create(
            state='NEW',
            checkin=today,
            checkout=tomorrow,
            room=self.room1,
            guests=2,
            customer=self.customer,
            total=30.0,
            code='TEST001'
        )

        percentage = self.calculate_occupancy_percentage()

        # 1 habitación ocupada de 3 total = 33.3%
        expected_percentage = round((1 / 3) * 100, 1)
        self.assertEqual(percentage, expected_percentage)
        print("Test de ocupación con 1 reserva confirmada: ", percentage)

    def test_occupancy_percentage_full_booking(self):
        """Test con todas las habitaciones ocupadas - debe ser 100%"""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Crear reservas para todas las habitaciones
        rooms = [self.room1, self.room2, self.room3]
        for i, room in enumerate(rooms):
            Booking.objects.create(
                state='NEW',
                checkin=today,
                checkout=tomorrow,
                room=room,
                guests=2,
                customer=self.customer,
                total=30.0,
                code=f'TEST00{i+1}'
            )

        percentage = self.calculate_occupancy_percentage()
        self.assertEqual(percentage, 100.0)
        print("Test de ocupación con todas las habitaciones ocupadas: ", percentage)

    def test_occupancy_percentage_cancelled_bookings_excluded(self):
        """Test que las reservas canceladas no se cuentan para ocupación"""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # Crear una reserva cancelada
        Booking.objects.create(
            state='DEL',
            checkin=today,
            checkout=tomorrow,
            room=self.room1,
            guests=2,
            customer=self.customer,
            total=30.0,
            code='TEST001'
        )

        percentage = self.calculate_occupancy_percentage()
        self.assertEqual(percentage, 0.0)
        print("Test de ocupación con reserva cancelada: ", percentage)

    def test_occupancy_percentage_past_bookings_excluded(self):
        """Test que las reservas pasadas no se cuentan para ocupación actual"""
        yesterday = date.today() - timedelta(days=1)
        today = date.today()

        # Crear una reserva que ya terminó (checkout = hoy, no incluye hoy)
        Booking.objects.create(
            state='NEW',
            checkin=yesterday,
            checkout=today,
            room=self.room1,
            guests=2,
            customer=self.customer,
            total=30.0,
            code='TEST001'
        )

        percentage = self.calculate_occupancy_percentage()
        self.assertEqual(percentage, 0.0)
        print("Test de ocupación con reserva pasada: ", percentage)

    def test_occupancy_percentage_future_bookings_excluded(self):
        """Test que las reservas futuras que no incluyen hoy no se cuentan"""
        tomorrow = date.today() + timedelta(days=1)
        day_after_tomorrow = date.today() + timedelta(days=2)

        # Crear una reserva futura que no incluye hoy
        Booking.objects.create(
            state='NEW',
            checkin=tomorrow,
            checkout=day_after_tomorrow,
            room=self.room1,
            guests=2,
            customer=self.customer,
            total=30.0,
            code='TEST001'
        )

        percentage = self.calculate_occupancy_percentage()
        self.assertEqual(percentage, 0.0)
        print("Test de ocupación con reserva futura que no incluye hoy: ", percentage)

    def test_occupancy_percentage_no_rooms(self):
        """Test del edge case sin habitaciones - debe ser 0%"""
        # Eliminar todas las habitaciones
        Room.objects.all().delete()

        percentage = self.calculate_occupancy_percentage()
        self.assertEqual(percentage, 0.0)
        print("Test de ocupación con 0 habitaciones: ", percentage)

    def test_occupancy_percentage_current_stay(self):
        """Test que las reservas actuales (checkin ayer, checkout mañana) se cuentan"""
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)

        # Crear una reserva que incluye hoy
        Booking.objects.create(
            state='NEW',
            checkin=yesterday,
            checkout=tomorrow,
            room=self.room1,
            guests=2,
            customer=self.customer,
            total=30.0,
            code='TEST001'
        )

        percentage = self.calculate_occupancy_percentage()
        expected_percentage = round((1 / 3) * 100, 1)
        self.assertEqual(percentage, expected_percentage)
        print("Test de ocupación con reserva actual (checkin ayer, checkout mañana): ", percentage)


class C_EditBookingDatesTestCase(TestCase):
    def setUp(self):
        """Configurar datos de prueba para edición de fechas de reserva"""
        self.client = Client()

        # Crear tipo de habitación
        self.room_type = Room_type.objects.create(
            name="Doble",
            price=50.0,
            max_guests=2
        )

        # Crear habitaciones de prueba
        self.room1 = Room.objects.create(
            name="Room 1.1",
            room_type=self.room_type,
            description="Habitación estándar"
        )

        self.room2 = Room.objects.create(
            name="Room 1.2",
            room_type=self.room_type,
            description="Habitación estándar"
        )

        # Crear cliente de prueba
        self.customer = Customer.objects.create(
            name="Nicolas Suarez",
            email="nasuarezro@unal.edu.co",
            phone="3228192983"
        )

        # Crear reserva base para las pruebas
        self.booking = Booking.objects.create(
            state='NEW',
            checkin=date.today() + timedelta(days=1),
            checkout=date.today() + timedelta(days=3),
            room=self.room1,
            guests=2,
            customer=self.customer,
            total=100.0,
            code='TEST001'
        )

    def test_edit_dates_successful(self):
        """Test de edición exitosa de fechas sin conflictos"""
        # Nuevas fechas sin conflictos
        new_checkin = date.today() + timedelta(days=5)
        new_checkout = date.today() + timedelta(days=7)

        # Datos del formulario
        form_data = {
            'checkin': new_checkin.strftime('%Y-%m-%d'),
            'checkout': new_checkout.strftime('%Y-%m-%d')
        }

        # Realizar la petición POST
        response = self.client.post(f'/booking/{self.booking.id}/edit-dates', form_data)

        # Verificar redirección exitosa
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        # Verificar que la reserva se actualizó
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.checkin, new_checkin)
        self.assertEqual(self.booking.checkout, new_checkout)

        # Verificar que el total se recalculó (2 días * 50.0 = 100.0)
        expected_total = 2 * self.room_type.price
        self.assertEqual(self.booking.total, expected_total)

        print(f"Test de edición exitosa: fechas actualizadas correctamente, nuevo total: {self.booking.total}")

    def test_edit_dates_with_conflict(self):
        """Test de edición con conflicto de disponibilidad"""
        # Crear otra reserva que cause conflicto
        conflict_checkin = date.today() + timedelta(days=5)
        conflict_checkout = date.today() + timedelta(days=7)

        conflicting_booking = Booking.objects.create(
            state='NEW',
            checkin=conflict_checkin,
            checkout=conflict_checkout,
            room=self.room1,  # Misma habitación
            guests=2,
            customer=self.customer,
            total=100.0,
            code='CONFLICT'
        )

        # Intentar editar fechas que se solapan con la reserva conflictiva
        form_data = {
            'checkin': (conflict_checkin + timedelta(days=1)).strftime('%Y-%m-%d'),
            'checkout': (conflict_checkout + timedelta(days=1)).strftime('%Y-%m-%d')
        }

        # Realizar la petición POST
        response = self.client.post(f'/booking/{self.booking.id}/edit-dates', form_data)

        # Verificar que NO redirige (hay error)
        self.assertEqual(response.status_code, 200)

        # Verificar que contiene el mensaje de error
        self.assertContains(response, 'No hay disponibilidad para las fechas seleccionadas')

        # Verificar que la reserva original NO se modificó
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.checkin, date.today() + timedelta(days=1))
        self.assertEqual(self.booking.checkout, date.today() + timedelta(days=3))

        print("Test de conflicto: error mostrado correctamente, reserva no modificada")

    def test_edit_dates_invalid_date_order(self):
        """Test con fecha de salida anterior o igual a fecha de entrada"""
        # Fechas inválidas (salida antes que entrada)
        invalid_checkin = date.today() + timedelta(days=5)
        invalid_checkout = date.today() + timedelta(days=4)  # Anterior a checkin

        form_data = {
            'checkin': invalid_checkin.strftime('%Y-%m-%d'),
            'checkout': invalid_checkout.strftime('%Y-%m-%d')
        }

        # Realizar la petición POST
        response = self.client.post(f'/booking/{self.booking.id}/edit-dates', form_data)

        # Verificar que NO redirige (hay error)
        self.assertEqual(response.status_code, 200)

        # Verificar que contiene el mensaje de error
        self.assertContains(response, 'La fecha de salida debe ser posterior a la fecha de entrada')

        # Verificar que la reserva original NO se modificó
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.checkin, date.today() + timedelta(days=1))
        self.assertEqual(self.booking.checkout, date.today() + timedelta(days=3))

        print("Test de fechas inválidas: error mostrado correctamente, reserva no modificada")

    def test_edit_dates_get_request(self):
        """Test del método GET para mostrar el formulario de edición"""
        response = self.client.get(f'/booking/{self.booking.id}/edit-dates')

        # Verificar que la página se carga correctamente
        self.assertEqual(response.status_code, 200)

        # Verificar que contiene la información de la reserva
        self.assertContains(response, self.booking.code)
        self.assertContains(response, self.booking.room.name)
        self.assertContains(response, self.booking.customer.name)

        # Verificar que contiene los campos del formulario
        self.assertContains(response, 'name="checkin"')
        self.assertContains(response, 'name="checkout"')

        print("Test GET: formulario de edición mostrado correctamente")

    def test_edit_dates_different_room_no_conflict(self):
        """Test de edición con fechas que no causan conflicto en otra habitación"""
        # Crear reserva en habitación diferente
        other_booking = Booking.objects.create(
            state='NEW',
            checkin=date.today() + timedelta(days=5),
            checkout=date.today() + timedelta(days=7),
            room=self.room2,  # Habitación diferente
            guests=2,
            customer=self.customer,
            total=100.0,
            code='OTHER'
        )

        # Editar fechas que se solapan con la otra reserva pero en habitación diferente
        form_data = {
            'checkin': (date.today() + timedelta(days=6)).strftime('%Y-%m-%d'),
            'checkout': (date.today() + timedelta(days=8)).strftime('%Y-%m-%d')
        }

        # Realizar la petición POST
        response = self.client.post(f'/booking/{self.booking.id}/edit-dates', form_data)

        # Verificar redirección exitosa (no hay conflicto)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        # Verificar que la reserva se actualizó
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.checkin, date.today() + timedelta(days=6))
        self.assertEqual(self.booking.checkout, date.today() + timedelta(days=8))

        print("Test sin conflicto en habitación diferente: edición exitosa")

#!/usr/bin/env python
"""
Sistema de Reservas de Hotel - Ejecución Principal
Ejecuta las funcionalidades principales del sistema de reservas de hotel.
"""
import os
import sys
from datetime import datetime

# Agregar src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from storage import JSONStorage
from hotel_service import HotelService
from customer_service import CustomerService
from reservation_service import ReservationService


def print_separator(title):
    """Imprimir separador con título."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def run_hotel_operations(hotel_service):
    """Ejecutar operaciones de hoteles del sistema de reservas."""
    print_separator("SISTEMA: OPERACIONES DE HOTELES")
    
    # Crear hoteles
    print("1. Creando hoteles...")
    hotel1 = hotel_service.create_hotel({
        'hotel_id': 'H001',
        'name': 'Hotel Grand Plaza',
        'location': 'New York',
        'total_rooms': 150,
        'available_rooms': 150
    })
    
    hotel2 = hotel_service.create_hotel({
        'hotel_id': 'H002',
        'name': 'Beach Resort Paradise',
        'location': 'Miami Beach',
        'total_rooms': 200,
        'available_rooms': 200
    })
    
    print(f"   - Creado: {hotel1.name} en {hotel1.location}")
    print(f"   - Creado: {hotel2.name} en {hotel2.location}")
    
    # Listar hoteles
    print("\n2. Listando todos los hoteles:")
    hotels = hotel_service.get_all_hotels()
    for hotel in hotels:
        print(f"   - {hotel.hotel_id}: {hotel.name} ({hotel.available_rooms}/{hotel.total_rooms} disponibles)")
    
    # Mostrar información detallada
    print("\n3. Información detallada del Hotel Grand Plaza:")
    info = hotel_service.display_hotel_info('H001')
    print(info)
    
    return hotels


def run_customer_operations(customer_service):
    """Ejecutar operaciones de clientes del sistema de reservas."""
    print_separator("SISTEMA: OPERACIONES DE CLIENTES")
    
    # Crear clientes
    print("1. Creando clientes...")
    customer1 = customer_service.create_customer(
        'C001', 'Carlos Parra', 'carlos@email.com', '555-0001'
    )
    
    customer2 = customer_service.create_customer(
        'C002', 'Ana Martinez', 'ana@email.com', '555-0002'
    )
    
    customer3 = customer_service.create_customer(
        'C003', 'Luis Rodriguez', 'luis@email.com', '555-0003'
    )
    
    print(f"   - Creado: {customer1.name} ({customer1.email})")
    print(f"   - Creado: {customer2.name} ({customer2.email})")
    print(f"   - Creado: {customer3.name} ({customer3.email})")
    
    # Buscar cliente por email
    print("\n2. Buscando cliente por email...")
    found_customer = customer_service.find_customer_by_email('ana@email.com')
    if found_customer:
        print(f"   - Encontrado: {found_customer.name}")
    
    # Listar todos los clientes
    print("\n3. Listando todos los clientes:")
    customers = customer_service.get_all_customers()
    for customer in customers:
        print(f"   - {customer.customer_id}: {customer.name} ({customer.email})")
    
    return customers


def run_reservation_operations(reservation_service, hotels, customers):
    """Ejecutar operaciones de reservas del sistema."""
    print_separator("SISTEMA: OPERACIONES DE RESERVAS")
    
    # Crear reservas
    print("1. Creando reservas...")
    
    reservation1 = reservation_service.create_reservation({
        'reservation_id': 'R001',
        'customer_id': 'C001',
        'hotel_id': 'H001',
        'check_in_date': '2024-12-15',
        'check_out_date': '2024-12-20'
    })
    
    reservation2 = reservation_service.create_reservation({
        'reservation_id': 'R002',
        'customer_id': 'C002',
        'hotel_id': 'H002',
        'check_in_date': '2024-12-18',
        'check_out_date': '2024-12-22'
    })
    
    reservation3 = reservation_service.create_reservation({
        'reservation_id': 'R003',
        'customer_id': 'C003',
        'hotel_id': 'H001',
        'check_in_date': '2024-12-25',
        'check_out_date': '2024-12-30'
    })
    
    print(f"   - Reserva {reservation1.reservation_id}: {reservation1.customer_id} en {reservation1.hotel_id}")
    print(f"   - Reserva {reservation2.reservation_id}: {reservation2.customer_id} en {reservation2.hotel_id}")
    print(f"   - Reserva {reservation3.reservation_id}: {reservation3.customer_id} en {reservation3.hotel_id}")
    
    # Mostrar información de reserva
    print("\n2. Información detallada de reserva R001:")
    info = reservation_service.display_reservation_info('R001')
    print(info)
    
    # Listar reservas activas
    print("\n3. Listando reservas activas:")
    active_reservations = reservation_service.get_active_reservations()
    for reservation in active_reservations:
        print(f"   - {reservation.reservation_id}: Cliente {reservation.customer_id} en Hotel {reservation.hotel_id}")
        print(f"     Fechas: {reservation.check_in_date} a {reservation.check_out_date}")
    
    # Reservas por cliente
    print("\n4. Reservas del cliente C001:")
    customer_reservations = reservation_service.get_reservations_by_customer('C001')
    for reservation in customer_reservations:
        print(f"   - {reservation.reservation_id} ({reservation.status.value})")
    
    # Cancelar una reserva
    print("\n5. Cancelando reserva R002...")
    cancelled = reservation_service.cancel_reservation('R002')
    if cancelled:
        print("   - Reserva R002 cancelada exitosamente")
        
        # Verificar que se canceló
        cancelled_reservation = reservation_service.get_reservation('R002')
        print(f"   - Estado actual: {cancelled_reservation.status.value}")
    
    return active_reservations


def show_data_persistence(storage):
    """Mostrar persistencia de datos del sistema."""
    print_separator("SISTEMA: PERSISTENCIA DE DATOS")
    
    print("1. Verificando archivos de datos creados:")
    data_files = ['hotels.json', 'customers.json', 'reservations.json']
    
    for file_name in data_files:
        file_path = os.path.join(storage.data_directory, file_name)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   - {file_name}: {size} bytes")
        else:
            print(f"   - {file_name}: No existe")
    
    # Contar registros
    print("\n2. Contando registros en la base de datos:")
    hotels_count = len(storage.load_hotels())
    customers_count = len(storage.load_customers())
    reservations_count = len(storage.load_reservations())
    
    print(f"   - Hoteles: {hotels_count}")
    print(f"   - Clientes: {customers_count}")
    print(f"   - Reservas: {reservations_count}")


def show_validation_features(reservation_service):
    """Mostrar características de validación del sistema."""
    print_separator("SISTEMA: VALIDACIÓN Y MANEJO DE ERRORES")
    
    print("1. Probando validación de reservas...")
    
    # Validar reserva válida
    is_valid, message = reservation_service.is_reservation_valid(
        'C001', 'H001', '2024-12-01', '2024-12-05'
    )
    print(f"   - Reserva válida: {is_valid} - {message}")
    
    # Validar reserva con fechas inválidas
    is_valid, message = reservation_service.is_reservation_valid(
        'C001', 'H001', '2024-12-05', '2024-12-01'  # Check-out antes que check-in
    )
    print(f"   - Fechas inválidas: {is_valid} - {message}")
    
    # Intentar crear reserva duplicada
    print("\n2. Probando manejo de errores...")
    try:
        reservation_service.create_reservation({
            'reservation_id': 'R001',  # ID ya existe
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-05'
        })
    except Exception as e:
        print(f"   - Error capturado correctamente: {type(e).__name__}")
        print(f"     Mensaje: {str(e)[:80]}...")


def clean_reservation_data():
    """Limpiar datos del sistema de reservas anterior."""
    import shutil
    if os.path.exists("reservation_system_data"):
        shutil.rmtree("reservation_system_data")
        print("   - Datos anteriores limpiados")


def main():
    """Función principal del sistema de reservas de hotel."""
    print("=" * 80)
    print(" SISTEMA DE RESERVAS DE HOTEL - EJECUCIÓN PRINCIPAL")
    print("=" * 80)
    print(f"Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Limpiar datos anteriores
    print("\nLimpiando datos anteriores...")
    clean_reservation_data()
    
    # Inicializar sistema
    print("\nInicializando sistema...")
    storage = JSONStorage("reservation_system_data")
    hotel_service = HotelService(storage)
    customer_service = CustomerService(storage)
    reservation_service = ReservationService(storage)
    
    try:
        # Ejecutar operaciones del sistema
        hotels = run_hotel_operations(hotel_service)
        customers = run_customer_operations(customer_service)
        reservations = run_reservation_operations(reservation_service, hotels, customers)
        show_data_persistence(storage)
        show_validation_features(reservation_service)
        
        # Resumen final
        print_separator("RESUMEN FINAL")
        print("SISTEMA DE RESERVAS EJECUTADO EXITOSAMENTE")
        print("\nFuncionalidades del sistema:")
        print("   - Creación y gestión de hoteles")
        print("   - Creación y gestión de clientes")
        print("   - Creación y gestión de reservas")
        print("   - Persistencia de datos en JSON")
        print("   - Validación de datos")
        print("   - Manejo de errores")
        print("   - Cancelación de reservas")
        print("   - Consultas y búsquedas")
        
        print(f"\nDatos guardados en: {storage.data_directory}/")
        print("El sistema está completamente funcional!")
        
    except Exception as e:
        print(f"\nERROR EN EL SISTEMA: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
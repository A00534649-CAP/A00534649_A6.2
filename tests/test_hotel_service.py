"""
Unit tests for the hotel_service module.
Tests HotelService class business logic operations.
"""
import unittest
import tempfile
import shutil
from unittest.mock import patch
from src.hotel_service import HotelService, HotelServiceError
from src.storage import JSONStorage, StorageError
from src.models import Customer, Reservation


class TestHotelService(unittest.TestCase):
    """Test cases for the HotelService class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = JSONStorage(self.test_dir)
        self.hotel_service = HotelService(self.storage)

    def tearDown(self):
        """Clean up after each test method."""
        if self.test_dir:
            shutil.rmtree(self.test_dir)

    # Hotel creation tests
    def test_create_hotel_success(self):
        """Test successful hotel creation."""
        hotel = self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Grand Hotel', 
            'location': 'New York',
            'total_rooms': 100,
            'available_rooms': 80
        })

        self.assertEqual(hotel.hotel_id, "H001")
        self.assertEqual(hotel.name, "Grand Hotel")
        self.assertEqual(hotel.location, "New York")
        self.assertEqual(hotel.total_rooms, 100)
        self.assertEqual(hotel.available_rooms, 80)

    def test_create_hotel_duplicate_id(self):
        """Test creating hotel with duplicate ID raises error."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel1',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel2',
            'location': 'CA',
            'total_rooms': 50,
            'available_rooms': 40
        })

        self.assertIn("Hotel with ID H001 already exists", str(context.exception))

    def test_create_hotel_invalid_data(self):
        """Test creating hotel with invalid data raises error."""
        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.create_hotel({
            'hotel_id': '',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        self.assertIn("Invalid hotel data", str(context.exception))

    def test_create_hotel_zero_total_rooms(self):
        """Test creating hotel with zero total rooms raises error."""
        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 0,
            'available_rooms': 0
        })

        self.assertIn("Invalid hotel data", str(context.exception))

    def test_create_hotel_negative_available_rooms(self):
        """Test creating hotel with negative available rooms raises error."""
        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': -10
        })

        self.assertIn("Invalid hotel data", str(context.exception))

    def test_create_hotel_available_exceeds_total(self):
        """Test creating hotel with available rooms exceeding total raises error."""
        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 150
        })

        self.assertIn("Invalid hotel data", str(context.exception))

    # Hotel retrieval tests
    def test_get_hotel_exists(self):
        """Test getting hotel that exists."""
        created_hotel = self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Grand Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })
        retrieved_hotel = self.hotel_service.get_hotel("H001")

        self.assertIsNotNone(retrieved_hotel)
        self.assertEqual(retrieved_hotel.hotel_id, created_hotel.hotel_id)
        self.assertEqual(retrieved_hotel.name, created_hotel.name)

    def test_get_hotel_not_exists(self):
        """Test getting hotel that doesn't exist."""
        retrieved_hotel = self.hotel_service.get_hotel("H999")
        self.assertIsNone(retrieved_hotel)

    def test_get_all_hotels_empty(self):
        """Test getting all hotels when none exist."""
        hotels = self.hotel_service.get_all_hotels()
        self.assertEqual(hotels, [])

    def test_get_all_hotels_multiple(self):
        """Test getting all hotels when multiple exist."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel1',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })
        self.hotel_service.create_hotel({
            'hotel_id': 'H002',
            'name': 'Hotel2',
            'location': 'CA',
            'total_rooms': 200,
            'available_rooms': 150
        })

        hotels = self.hotel_service.get_all_hotels()
        self.assertEqual(len(hotels), 2)

        hotel_ids = [h.hotel_id for h in hotels]
        self.assertIn("H001", hotel_ids)
        self.assertIn("H002", hotel_ids)

    # Hotel update tests
    def test_update_hotel_name(self):
        """Test updating hotel name."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Old Name',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        updated_hotel = self.hotel_service.update_hotel('H001', {'name': 'New Name'})
        self.assertEqual(updated_hotel.name, "New Name")
        self.assertEqual(updated_hotel.location, "NY")  # Unchanged

    def test_update_hotel_all_fields(self):
        """Test updating all hotel fields."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Old Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        updated_hotel = self.hotel_service.update_hotel('H001', {'name': 'New Hotel', 'location': 'CA', 'total_rooms': 200, 'available_rooms': 150})

        self.assertEqual(updated_hotel.name, "New Hotel")
        self.assertEqual(updated_hotel.location, "CA")
        self.assertEqual(updated_hotel.total_rooms, 200)
        self.assertEqual(updated_hotel.available_rooms, 150)

    def test_update_hotel_not_exists(self):
        """Test updating hotel that doesn't exist raises error."""
        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.update_hotel('H999', {'name': 'New Name'})

        self.assertIn("Hotel with ID H999 not found", str(context.exception))

    def test_update_hotel_invalid_data(self):
        """Test updating hotel with invalid data raises error."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.update_hotel('H001', {'available_rooms': -10})

        self.assertIn("Invalid hotel data", str(context.exception))

    # Hotel deletion tests
    def test_delete_hotel_success(self):
        """Test successful hotel deletion."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        result = self.hotel_service.delete_hotel("H001")
        self.assertTrue(result)

        retrieved_hotel = self.hotel_service.get_hotel("H001")
        self.assertIsNone(retrieved_hotel)

    def test_delete_hotel_not_exists(self):
        """Test deleting hotel that doesn't exist."""
        result = self.hotel_service.delete_hotel("H999")
        self.assertFalse(result)

    def test_delete_hotel_with_active_reservations(self):
        """Test deleting hotel with active reservations raises error."""
        # Create hotel
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        # Create customer and reservation
        customer = Customer("C001", "John", "john@test.com", "123")
        self.storage.save_customer(customer)

        reservation = Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03")
        self.storage.save_reservation(reservation)

        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.delete_hotel("H001")

        self.assertIn("has active reservations", str(context.exception))

    def test_delete_hotel_with_cancelled_reservations(self):
        """Test deleting hotel with only cancelled reservations succeeds."""
        # Create hotel
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        # Create customer and cancelled reservation
        customer = Customer("C001", "John", "john@test.com", "123")
        self.storage.save_customer(customer)

        reservation = Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03")
        reservation.cancel()
        self.storage.save_reservation(reservation)

        result = self.hotel_service.delete_hotel("H001")
        self.assertTrue(result)

    # Room reservation tests
    def test_reserve_room_success(self):
        """Test successful room reservation."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        result = self.hotel_service.reserve_room("H001")
        self.assertTrue(result)

        hotel = self.hotel_service.get_hotel("H001")
        self.assertEqual(hotel.available_rooms, 79)

    def test_reserve_room_no_availability(self):
        """Test room reservation when no rooms available."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 0
        })

        result = self.hotel_service.reserve_room("H001")
        self.assertFalse(result)

        hotel = self.hotel_service.get_hotel("H001")
        self.assertEqual(hotel.available_rooms, 0)

    def test_reserve_room_hotel_not_exists(self):
        """Test room reservation for non-existent hotel raises error."""
        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.reserve_room("H999")

        self.assertIn("Hotel with ID H999 not found", str(context.exception))

    def test_cancel_reservation_room_success(self):
        """Test successful room cancellation."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        result = self.hotel_service.cancel_reservation_room("H001")
        self.assertTrue(result)

        hotel = self.hotel_service.get_hotel("H001")
        self.assertEqual(hotel.available_rooms, 81)

    def test_cancel_reservation_room_full_capacity(self):
        """Test room cancellation when hotel is at full capacity."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 100
        })

        result = self.hotel_service.cancel_reservation_room("H001")
        self.assertFalse(result)

        hotel = self.hotel_service.get_hotel("H001")
        self.assertEqual(hotel.available_rooms, 100)

    def test_cancel_reservation_room_hotel_not_exists(self):
        """Test room cancellation for non-existent hotel raises error."""
        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.cancel_reservation_room("H999")

        self.assertIn("Hotel with ID H999 not found", str(context.exception))

    # Display and utility tests
    def test_display_hotel_info(self):
        """Test displaying hotel information."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Grand Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        info = self.hotel_service.display_hotel_info("H001")

        self.assertIn("Hotel Information:", info)
        self.assertIn("ID: H001", info)
        self.assertIn("Name: Grand Hotel", info)
        self.assertIn("Location: NY", info)
        self.assertIn("Total Rooms: 100", info)
        self.assertIn("Available Rooms: 80", info)
        self.assertIn("Occupancy Rate: 20.0%", info)

    def test_display_hotel_info_not_exists(self):
        """Test displaying info for non-existent hotel raises error."""
        with self.assertRaises(HotelServiceError) as context:
            self.hotel_service.display_hotel_info("H999")

        self.assertIn("Hotel with ID H999 not found", str(context.exception))

    def test_get_hotel_availability(self):
        """Test getting hotel availability."""
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        })

        availability = self.hotel_service.get_hotel_availability("H001")
        self.assertEqual(availability, 80)

    def test_get_hotel_availability_not_exists(self):
        """Test getting availability for non-existent hotel."""
        availability = self.hotel_service.get_hotel_availability("H999")
        self.assertIsNone(availability)

    def test_create_hotel_storage_error(self):
        """Test create hotel with storage error."""
        with patch.object(self.storage, 'save_hotel', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.create_hotel({
                    'hotel_id': 'H001',
                    'name': 'Hotel',
                    'location': 'NY',
                    'total_rooms': 100,
                    'available_rooms': 100
                })
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_hotel_storage_error(self):
        """Test get hotel with storage error."""
        with patch.object(self.storage, 'find_hotel_by_id', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.get_hotel("H001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_all_hotels_storage_error(self):
        """Test get all hotels with storage error."""
        with patch.object(self.storage, 'load_hotels', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.get_all_hotels()
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_update_hotel_storage_error(self):
        """Test update hotel with storage error."""
        # Create hotel first
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 100
        })
        
        with patch.object(self.storage, 'save_hotel', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.update_hotel("H001", {"name": "New Hotel"})
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_delete_hotel_storage_error(self):
        """Test delete hotel with storage error."""
        with patch.object(self.storage, 'delete_hotel', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.delete_hotel("H001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_reserve_room_storage_error(self):
        """Test reserve room with storage error."""
        # Create hotel first
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 100
        })
        
        with patch.object(self.storage, 'save_hotel', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.reserve_room("H001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_cancel_reservation_room_storage_error(self):
        """Test cancel reservation room with storage error."""
        # Create hotel first
        self.hotel_service.create_hotel({
            'hotel_id': 'H001',
            'name': 'Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 90
        })
        
        with patch.object(self.storage, 'save_hotel', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.cancel_reservation_room("H001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_display_hotel_info_storage_error(self):
        """Test display hotel info with storage error."""
        with patch.object(self.storage, 'find_hotel_by_id', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.display_hotel_info("H001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_hotel_availability_storage_error(self):
        """Test get hotel availability with storage error."""
        with patch.object(self.storage, 'find_hotel_by_id', side_effect=StorageError("Storage failed")):
            with self.assertRaises(HotelServiceError) as context:
                self.hotel_service.get_hotel_availability("H001")
            self.assertIn("Storage error: Storage failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for the reservation_service module.
Tests ReservationService class business logic operations.
"""
import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch
from src.reservation_service import ReservationService, ReservationServiceError
from src.storage import JSONStorage, StorageError
from src.models import Hotel, Customer, ReservationStatus
from src.hotel_service import HotelServiceError
from src.customer_service import CustomerServiceError


class TestReservationService(unittest.TestCase):
    """Test cases for the ReservationService class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = JSONStorage(self.test_dir)
        self.reservation_service = ReservationService(self.storage)

        # Create test hotel and customer
        self.hotel = Hotel("H001", "Grand Hotel", "NY", 100, 50)
        self.customer = Customer("C001", "John Doe", "john@example.com", "123-456-7890")
        self.storage.save_hotel(self.hotel)
        self.storage.save_customer(self.customer)

    def tearDown(self):
        """Clean up after each test method."""
        if self.test_dir:
            shutil.rmtree(self.test_dir)

    # Reservation creation tests
    def test_create_reservation_success(self):
        """Test successful reservation creation."""
        reservation = self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })

        self.assertEqual(reservation.reservation_id, "R001")
        self.assertEqual(reservation.customer_id, "C001")
        self.assertEqual(reservation.hotel_id, "H001")
        self.assertEqual(reservation.check_in_date, "2024-12-01")
        self.assertEqual(reservation.check_out_date, "2024-12-03")
        self.assertEqual(reservation.status, ReservationStatus.ACTIVE)

        # Verify room was reserved
        updated_hotel = self.storage.find_hotel_by_id("H001")
        self.assertEqual(updated_hotel.available_rooms, 49)

    def test_create_reservation_duplicate_id(self):
        """Test creating reservation with duplicate ID raises error."""
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })

        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-05',
            'check_out_date': '2024-12-07'
        })

        self.assertIn("Reservation with ID R001 already exists", str(context.exception))

    def test_create_reservation_customer_not_exists(self):
        """Test creating reservation with non-existent customer raises error."""
        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C999',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })

        self.assertIn("Customer with ID C999 not found", str(context.exception))

    def test_create_reservation_hotel_not_exists(self):
        """Test creating reservation with non-existent hotel raises error."""
        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H999',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })

        self.assertIn("Hotel with ID H999 not found", str(context.exception))

    def test_create_reservation_no_rooms_available(self):
        """Test creating reservation when no rooms available raises error."""
        # Create hotel with no available rooms
        full_hotel = Hotel("H002", "Full Hotel", "CA", 100, 0)
        self.storage.save_hotel(full_hotel)

        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H002',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })

        self.assertIn("No rooms available at hotel H002", str(context.exception))

    def test_create_reservation_invalid_dates(self):
        """Test creating reservation with invalid dates raises error."""
        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-03',
            'check_out_date': '2024-12-01'
        })

        self.assertIn("Invalid reservation data", str(context.exception))

    def test_create_reservation_invalid_date_format(self):
        """Test creating reservation with invalid date format raises error."""
        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024/12/01',
            'check_out_date': '2024-12-03'
        })

        self.assertIn("Invalid reservation data", str(context.exception))

    def test_create_reservation_empty_fields(self):
        """Test creating reservation with empty fields raises error."""
        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.create_reservation({
                'reservation_id': '',
                'customer_id': 'C001',
                'hotel_id': 'H001',
                'check_in_date': '2024-12-01',
                'check_out_date': '2024-12-03'
            })

        self.assertIn("Invalid reservation data", str(context.exception))

    # Reservation retrieval tests
    def test_get_reservation_exists(self):
        """Test getting reservation that exists."""
        created_reservation = self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })
        retrieved_reservation = self.reservation_service.get_reservation("R001")

        self.assertIsNotNone(retrieved_reservation)
        self.assertEqual(retrieved_reservation.reservation_id, created_reservation.reservation_id)

    def test_get_reservation_not_exists(self):
        """Test getting reservation that doesn't exist."""
        retrieved_reservation = self.reservation_service.get_reservation("R999")
        self.assertIsNone(retrieved_reservation)

    def test_get_all_reservations_empty(self):
        """Test getting all reservations when none exist."""
        reservations = self.reservation_service.get_all_reservations()
        self.assertEqual(reservations, [])

    def test_get_all_reservations_multiple(self):
        """Test getting all reservations when multiple exist."""
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })
        self.reservation_service.create_reservation({
            'reservation_id': 'R002',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-05',
            'check_out_date': '2024-12-07'
        })

        reservations = self.reservation_service.get_all_reservations()
        self.assertEqual(len(reservations), 2)

    # Reservation cancellation tests
    def test_cancel_reservation_success(self):
        """Test successful reservation cancellation."""
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })

        # Verify hotel has 49 available rooms after reservation
        hotel_before = self.storage.find_hotel_by_id("H001")
        self.assertEqual(hotel_before.available_rooms, 49)

        result = self.reservation_service.cancel_reservation("R001")
        self.assertTrue(result)

        # Verify reservation is cancelled
        reservation = self.storage.find_reservation_by_id("R001")
        self.assertEqual(reservation.status, ReservationStatus.CANCELLED)

        # Verify room is freed
        hotel_after = self.storage.find_hotel_by_id("H001")
        self.assertEqual(hotel_after.available_rooms, 50)

    def test_cancel_reservation_not_exists(self):
        """Test cancelling reservation that doesn't exist raises error."""
        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.cancel_reservation("R999")

        self.assertIn("Reservation with ID R999 not found", str(context.exception))

    def test_cancel_reservation_already_cancelled(self):
        """Test cancelling already cancelled reservation returns False."""
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })

        # Cancel first time
        result1 = self.reservation_service.cancel_reservation("R001")
        self.assertTrue(result1)

        # Cancel second time
        result2 = self.reservation_service.cancel_reservation("R001")
        self.assertFalse(result2)

    # Display and utility tests
    def test_display_reservation_info(self):
        """Test displaying reservation information."""
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })

        info = self.reservation_service.display_reservation_info("R001")

        self.assertIn("Reservation Information:", info)
        self.assertIn("ID: R001", info)
        self.assertIn("Customer: John Doe (ID: C001)", info)
        self.assertIn("Hotel: Grand Hotel (ID: H001)", info)
        self.assertIn("Check-in Date: 2024-12-01", info)
        self.assertIn("Check-out Date: 2024-12-03", info)
        self.assertIn("Stay Duration: 2 nights", info)
        self.assertIn("Status: Active", info)

    def test_display_reservation_info_not_exists(self):
        """Test displaying info for non-existent reservation raises error."""
        with self.assertRaises(ReservationServiceError) as context:
            self.reservation_service.display_reservation_info("R999")

        self.assertIn("Reservation with ID R999 not found", str(context.exception))

    def test_get_reservations_by_customer(self):
        """Test getting reservations by customer ID."""
        # Create second customer
        customer2 = Customer("C002", "Jane Doe", "jane@example.com", "987-654-3210")
        self.storage.save_customer(customer2)

        # Create reservations for different customers
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })
        self.reservation_service.create_reservation({
            'reservation_id': 'R002',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-05',
            'check_out_date': '2024-12-07'
        })
        self.reservation_service.create_reservation({
            'reservation_id': 'R003',
            'customer_id': 'C002',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-10',
            'check_out_date': '2024-12-12'
        })

        customer1_reservations = self.reservation_service.get_reservations_by_customer("C001")
        self.assertEqual(len(customer1_reservations), 2)

        reservation_ids = [r.reservation_id for r in customer1_reservations]
        self.assertIn("R001", reservation_ids)
        self.assertIn("R002", reservation_ids)

    def test_get_reservations_by_hotel(self):
        """Test getting reservations by hotel ID."""
        # Create second hotel
        hotel2 = Hotel("H002", "Beach Resort", "CA", 100, 50)
        self.storage.save_hotel(hotel2)

        # Create reservations for different hotels
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })
        self.reservation_service.create_reservation({
            'reservation_id': 'R002',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-05',
            'check_out_date': '2024-12-07'
        })
        self.reservation_service.create_reservation({
            'reservation_id': 'R003',
            'customer_id': 'C001',
            'hotel_id': 'H002',
            'check_in_date': '2024-12-10',
            'check_out_date': '2024-12-12'
        })

        hotel1_reservations = self.reservation_service.get_reservations_by_hotel("H001")
        self.assertEqual(len(hotel1_reservations), 2)

        reservation_ids = [r.reservation_id for r in hotel1_reservations]
        self.assertIn("R001", reservation_ids)
        self.assertIn("R002", reservation_ids)

    def test_get_active_reservations(self):
        """Test getting only active reservations."""
        # Create reservations
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })
        self.reservation_service.create_reservation({
            'reservation_id': 'R002',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-05',
            'check_out_date': '2024-12-07'
        })

        # Cancel one reservation
        self.reservation_service.cancel_reservation("R001")

        active_reservations = self.reservation_service.get_active_reservations()
        self.assertEqual(len(active_reservations), 1)
        self.assertEqual(active_reservations[0].reservation_id, "R002")

    # Validation tests
    def test_is_reservation_valid_success(self):
        """Test reservation validation with valid data."""
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        later_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

        is_valid, message = self.reservation_service.is_reservation_valid(
            "C001", "H001", future_date, later_date
        )

        self.assertTrue(is_valid)
        self.assertEqual(message, "Reservation is valid")

    def test_is_reservation_valid_customer_not_exists(self):
        """Test reservation validation with non-existent customer."""
        is_valid, message = self.reservation_service.is_reservation_valid(
            "C999", "H001", "2024-12-01", "2024-12-03"
        )

        self.assertFalse(is_valid)
        self.assertIn("Customer with ID C999 not found", message)

    def test_is_reservation_valid_hotel_not_exists(self):
        """Test reservation validation with non-existent hotel."""
        is_valid, message = self.reservation_service.is_reservation_valid(
            "C001", "H999", "2024-12-01", "2024-12-03"
        )

        self.assertFalse(is_valid)
        self.assertIn("Hotel with ID H999 not found", message)

    def test_is_reservation_valid_no_rooms_available(self):
        """Test reservation validation when no rooms available."""
        # Create hotel with no available rooms
        full_hotel = Hotel("H002", "Full Hotel", "CA", 100, 0)
        self.storage.save_hotel(full_hotel)

        is_valid, message = self.reservation_service.is_reservation_valid(
            "C001", "H002", "2024-12-01", "2024-12-03"
        )

        self.assertFalse(is_valid)
        self.assertIn("No rooms available at hotel H002", message)

    def test_is_reservation_valid_invalid_dates(self):
        """Test reservation validation with invalid dates."""
        is_valid, message = self.reservation_service.is_reservation_valid(
            "C001", "H001", "2024-12-03", "2024-12-01"
        )

        self.assertFalse(is_valid)
        self.assertIn("Check-out date must be after check-in date", message)

    def test_is_reservation_valid_past_date(self):
        """Test reservation validation with past check-in date."""
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        is_valid, message = self.reservation_service.is_reservation_valid(
            "C001", "H001", past_date, future_date
        )

        self.assertFalse(is_valid)
        self.assertIn("Check-in date cannot be in the past", message)

    def test_is_reservation_valid_invalid_date_format(self):
        """Test reservation validation with invalid date format."""
        is_valid, message = self.reservation_service.is_reservation_valid(
            "C001", "H001", "2024/12/01", "2024-12-03"
        )

        self.assertFalse(is_valid)
        self.assertIn("Invalid date format", message)

    def test_create_reservation_hotel_service_error(self):
        """Test create reservation with HotelServiceError."""
        with patch.object(self.reservation_service.hotel_service, 'reserve_room', side_effect=HotelServiceError("Hotel error")):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.create_reservation({
                    'reservation_id': 'R001',
                    'customer_id': 'C001',
                    'hotel_id': 'H001',
                    'check_in_date': '2024-12-01',
                    'check_out_date': '2024-12-03'
                })
            self.assertIn("Service error: Hotel error", str(context.exception))

    def test_get_reservation_storage_error(self):
        """Test get reservation with storage error."""
        with patch.object(self.storage, 'find_reservation_by_id', side_effect=StorageError("Storage failed")):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.get_reservation("R001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_all_reservations_storage_error(self):
        """Test get all reservations with storage error."""
        with patch.object(self.storage, 'load_reservations', side_effect=StorageError("Storage failed")):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.get_all_reservations()
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_cancel_reservation_storage_error(self):
        """Test cancel reservation with storage error."""
        # Create reservation first
        self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })
        
        with patch.object(self.storage, 'save_reservation', side_effect=StorageError("Storage failed")):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.cancel_reservation("R001")
            self.assertIn("Service error: Storage failed", str(context.exception))

    def test_display_reservation_info_storage_error(self):
        """Test display reservation info with storage error."""
        with patch.object(self.storage, 'find_reservation_by_id', side_effect=StorageError("Storage failed")):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.display_reservation_info("R001")
            self.assertIn("Service error: Storage failed", str(context.exception))

    def test_get_reservations_by_customer_storage_error(self):
        """Test get reservations by customer with storage error."""
        with patch.object(self.storage, 'get_reservations_by_customer', side_effect=StorageError("Storage failed")):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.get_reservations_by_customer("C001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_reservations_by_hotel_storage_error(self):
        """Test get reservations by hotel with storage error."""
        with patch.object(self.storage, 'get_reservations_by_hotel', side_effect=StorageError("Storage failed")):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.get_reservations_by_hotel("H001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_active_reservations_storage_error(self):
        """Test get active reservations with storage error."""
        with patch.object(self.storage, 'load_reservations', side_effect=StorageError("Storage failed")):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.get_active_reservations()
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_is_reservation_valid_service_error(self):
        """Test is reservation valid with service error."""
        with patch.object(self.reservation_service.hotel_service, 'get_hotel', side_effect=HotelServiceError("Hotel error")):
            is_valid, message = self.reservation_service.is_reservation_valid(
                "C001", "H001", "2024-12-01", "2024-12-03"
            )
            self.assertFalse(is_valid)
            self.assertIn("Hotel error", message)

    def test_create_reservation_room_reserve_fails(self):
        """Test create reservation when room reservation fails."""
        # Mock reserve_room to return False
        with patch.object(self.reservation_service.hotel_service, 'reserve_room', return_value=False):
            with self.assertRaises(ReservationServiceError) as context:
                self.reservation_service.create_reservation({
                    'reservation_id': 'R001',
                    'customer_id': 'C001',
                    'hotel_id': 'H001',
                    'check_in_date': '2024-12-01',
                    'check_out_date': '2024-12-03'
                })
            self.assertIn("Failed to reserve room at hotel H001", str(context.exception))

    def test_cancel_reservation_room_free_fails(self):
        """Test cancel reservation when freeing room fails."""
        # Create a reservation first
        reservation = self.reservation_service.create_reservation({
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03'
        })
        
        # Mock cancel_reservation_room to return False (should print warning)
        with patch.object(self.reservation_service.hotel_service, 'cancel_reservation_room', return_value=False):
            with patch('builtins.print') as mock_print:
                result = self.reservation_service.cancel_reservation("R001")
                self.assertTrue(result)  # Should still succeed
                mock_print.assert_called_with("Warning: Could not free room for hotel H001")


if __name__ == '__main__':
    unittest.main()

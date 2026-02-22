"""
Unit tests for the models module.
Tests Hotel, Customer, and Reservation classes.
"""
import unittest
from datetime import datetime
from src.models import Hotel, Customer, Reservation, ReservationStatus


class TestHotel(unittest.TestCase):
    """Test cases for the Hotel class."""

    def test_hotel_creation_valid(self):
        """Test creating a valid hotel."""
        hotel = Hotel(
            hotel_id="H001",
            name="Grand Hotel",
            location="New York",
            total_rooms=100,
            available_rooms=80
        )
        self.assertEqual(hotel.hotel_id, "H001")
        self.assertEqual(hotel.name, "Grand Hotel")
        self.assertEqual(hotel.location, "New York")
        self.assertEqual(hotel.total_rooms, 100)
        self.assertEqual(hotel.available_rooms, 80)

    def test_hotel_creation_empty_id(self):
        """Test creating hotel with empty ID raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Hotel(
                hotel_id="",
                name="Grand Hotel",
                location="New York",
                total_rooms=100,
                available_rooms=80
            )
        self.assertIn("Hotel ID cannot be empty", str(context.exception))

    def test_hotel_creation_empty_name(self):
        """Test creating hotel with empty name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Hotel(
                hotel_id="H001",
                name="",
                location="New York",
                total_rooms=100,
                available_rooms=80
            )
        self.assertIn("Hotel name cannot be empty", str(context.exception))

    def test_hotel_creation_empty_location(self):
        """Test creating hotel with empty location raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Hotel(
                hotel_id="H001",
                name="Grand Hotel",
                location="",
                total_rooms=100,
                available_rooms=80
            )
        self.assertIn("Hotel location cannot be empty", str(context.exception))

    def test_hotel_creation_zero_total_rooms(self):
        """Test creating hotel with zero total rooms raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Hotel(
                hotel_id="H001",
                name="Grand Hotel",
                location="New York",
                total_rooms=0,
                available_rooms=0
            )
        self.assertIn("Total rooms must be greater than 0", str(context.exception))

    def test_hotel_creation_negative_total_rooms(self):
        """Test creating hotel with negative total rooms raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Hotel(
                hotel_id="H001",
                name="Grand Hotel",
                location="New York",
                total_rooms=-10,
                available_rooms=0
            )
        self.assertIn("Total rooms must be greater than 0", str(context.exception))

    def test_hotel_creation_negative_available_rooms(self):
        """Test creating hotel with negative available rooms raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Hotel(
                hotel_id="H001",
                name="Grand Hotel",
                location="New York",
                total_rooms=100,
                available_rooms=-5
            )
        self.assertIn("Available rooms cannot be negative", str(context.exception))

    def test_hotel_creation_available_exceeds_total(self):
        """Test creating hotel with available rooms exceeding total raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Hotel(
                hotel_id="H001",
                name="Grand Hotel",
                location="New York",
                total_rooms=100,
                available_rooms=150
            )
        self.assertIn("Available rooms cannot exceed total rooms", str(context.exception))

    def test_hotel_reserve_room_success(self):
        """Test successful room reservation."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 50)
        result = hotel.reserve_room()
        self.assertTrue(result)
        self.assertEqual(hotel.available_rooms, 49)

    def test_hotel_reserve_room_no_availability(self):
        """Test room reservation when no rooms available."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 0)
        result = hotel.reserve_room()
        self.assertFalse(result)
        self.assertEqual(hotel.available_rooms, 0)

    def test_hotel_cancel_reservation_success(self):
        """Test successful reservation cancellation."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 50)
        result = hotel.cancel_reservation()
        self.assertTrue(result)
        self.assertEqual(hotel.available_rooms, 51)

    def test_hotel_cancel_reservation_full_capacity(self):
        """Test reservation cancellation when hotel is at full capacity."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 100)
        result = hotel.cancel_reservation()
        self.assertFalse(result)
        self.assertEqual(hotel.available_rooms, 100)

    def test_hotel_to_dict(self):
        """Test converting hotel to dictionary."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 80)
        expected = {
            'hotel_id': 'H001',
            'name': 'Grand Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        }
        self.assertEqual(hotel.to_dict(), expected)

    def test_hotel_from_dict(self):
        """Test creating hotel from dictionary."""
        data = {
            'hotel_id': 'H001',
            'name': 'Grand Hotel',
            'location': 'NY',
            'total_rooms': 100,
            'available_rooms': 80
        }
        hotel = Hotel.from_dict(data)
        self.assertEqual(hotel.hotel_id, 'H001')
        self.assertEqual(hotel.name, 'Grand Hotel')
        self.assertEqual(hotel.location, 'NY')
        self.assertEqual(hotel.total_rooms, 100)
        self.assertEqual(hotel.available_rooms, 80)


class TestCustomer(unittest.TestCase):
    """Test cases for the Customer class."""

    def test_customer_creation_valid(self):
        """Test creating a valid customer."""
        customer = Customer(
            customer_id="C001",
            name="John Doe",
            email="john@example.com",
            phone="123-456-7890"
        )
        self.assertEqual(customer.customer_id, "C001")
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.email, "john@example.com")
        self.assertEqual(customer.phone, "123-456-7890")

    def test_customer_creation_empty_id(self):
        """Test creating customer with empty ID raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Customer(
                customer_id="",
                name="John Doe",
                email="john@example.com",
                phone="123-456-7890"
            )
        self.assertIn("Customer ID cannot be empty", str(context.exception))

    def test_customer_creation_empty_name(self):
        """Test creating customer with empty name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Customer(
                customer_id="C001",
                name="",
                email="john@example.com",
                phone="123-456-7890"
            )
        self.assertIn("Customer name cannot be empty", str(context.exception))

    def test_customer_creation_empty_email(self):
        """Test creating customer with empty email raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Customer(
                customer_id="C001",
                name="John Doe",
                email="",
                phone="123-456-7890"
            )
        self.assertIn("Customer email cannot be empty", str(context.exception))

    def test_customer_creation_invalid_email_format(self):
        """Test creating customer with invalid email format raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Customer(
                customer_id="C001",
                name="John Doe",
                email="invalid-email",
                phone="123-456-7890"
            )
        self.assertIn("Invalid email format", str(context.exception))

    def test_customer_creation_invalid_email_no_domain(self):
        """Test creating customer with invalid email (no domain) raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Customer(
                customer_id="C001",
                name="John Doe",
                email="john@",
                phone="123-456-7890"
            )
        self.assertIn("Invalid email format", str(context.exception))

    def test_customer_creation_empty_phone(self):
        """Test creating customer with empty phone raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Customer(
                customer_id="C001",
                name="John Doe",
                email="john@example.com",
                phone=""
            )
        self.assertIn("Customer phone cannot be empty", str(context.exception))

    def test_customer_valid_email_formats(self):
        """Test various valid email formats."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "user123@test-domain.com",
            "a@b.co"
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                customer = Customer("C001", "John", email, "123")
                self.assertEqual(customer.email, email)

    def test_customer_to_dict(self):
        """Test converting customer to dictionary."""
        customer = Customer("C001", "John Doe", "john@example.com", "123-456-7890")
        expected = {
            'customer_id': 'C001',
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '123-456-7890'
        }
        self.assertEqual(customer.to_dict(), expected)

    def test_customer_from_dict(self):
        """Test creating customer from dictionary."""
        data = {
            'customer_id': 'C001',
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '123-456-7890'
        }
        customer = Customer.from_dict(data)
        self.assertEqual(customer.customer_id, 'C001')
        self.assertEqual(customer.name, 'John Doe')
        self.assertEqual(customer.email, 'john@example.com')
        self.assertEqual(customer.phone, '123-456-7890')


class TestReservation(unittest.TestCase):
    """Test cases for the Reservation class."""

    def test_reservation_creation_valid(self):
        """Test creating a valid reservation."""
        reservation = Reservation(
            reservation_id="R001",
            customer_id="C001",
            hotel_id="H001",
            check_in_date="2024-12-01",
            check_out_date="2024-12-03"
        )
        self.assertEqual(reservation.reservation_id, "R001")
        self.assertEqual(reservation.customer_id, "C001")
        self.assertEqual(reservation.hotel_id, "H001")
        self.assertEqual(reservation.check_in_date, "2024-12-01")
        self.assertEqual(reservation.check_out_date, "2024-12-03")
        self.assertEqual(reservation.status, ReservationStatus.ACTIVE)

    def test_reservation_creation_empty_id(self):
        """Test creating reservation with empty ID raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Reservation(
                reservation_id="",
                customer_id="C001",
                hotel_id="H001",
                check_in_date="2024-12-01",
                check_out_date="2024-12-03"
            )
        self.assertIn("Reservation ID cannot be empty", str(context.exception))

    def test_reservation_creation_empty_customer_id(self):
        """Test creating reservation with empty customer ID raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Reservation(
                reservation_id="R001",
                customer_id="",
                hotel_id="H001",
                check_in_date="2024-12-01",
                check_out_date="2024-12-03"
            )
        self.assertIn("Customer ID cannot be empty", str(context.exception))

    def test_reservation_creation_empty_hotel_id(self):
        """Test creating reservation with empty hotel ID raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Reservation(
                reservation_id="R001",
                customer_id="C001",
                hotel_id="",
                check_in_date="2024-12-01",
                check_out_date="2024-12-03"
            )
        self.assertIn("Hotel ID cannot be empty", str(context.exception))

    def test_reservation_creation_empty_check_in_date(self):
        """Test creating reservation with empty check-in date raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Reservation(
                reservation_id="R001",
                customer_id="C001",
                hotel_id="H001",
                check_in_date="",
                check_out_date="2024-12-03"
            )
        self.assertIn("Check-in date cannot be empty", str(context.exception))

    def test_reservation_creation_empty_check_out_date(self):
        """Test creating reservation with empty check-out date raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Reservation(
                reservation_id="R001",
                customer_id="C001",
                hotel_id="H001",
                check_in_date="2024-12-01",
                check_out_date=""
            )
        self.assertIn("Check-out date cannot be empty", str(context.exception))

    def test_reservation_creation_invalid_date_format(self):
        """Test creating reservation with invalid date format raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Reservation(
                reservation_id="R001",
                customer_id="C001",
                hotel_id="H001",
                check_in_date="2024/12/01",
                check_out_date="2024-12-03"
            )
        self.assertIn("Invalid date format", str(context.exception))

    def test_reservation_creation_check_out_before_check_in(self):
        """Test creating reservation with check-out before check-in raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Reservation(
                reservation_id="R001",
                customer_id="C001",
                hotel_id="H001",
                check_in_date="2024-12-03",
                check_out_date="2024-12-01"
            )
        self.assertIn("Check-out date must be after check-in date", str(context.exception))

    def test_reservation_creation_same_dates(self):
        """Test creating reservation with same check-in and check-out dates raises ValueError."""
        with self.assertRaises(ValueError) as context:
            Reservation(
                reservation_id="R001",
                customer_id="C001",
                hotel_id="H001",
                check_in_date="2024-12-01",
                check_out_date="2024-12-01"
            )
        self.assertIn("Check-out date must be after check-in date", str(context.exception))

    def test_reservation_cancel(self):
        """Test cancelling a reservation."""
        reservation = Reservation(
            "R001", "C001", "H001", "2024-12-01", "2024-12-03"
        )
        self.assertTrue(reservation.is_active())

        reservation.cancel()
        self.assertEqual(reservation.status, ReservationStatus.CANCELLED)
        self.assertFalse(reservation.is_active())

    def test_reservation_to_dict(self):
        """Test converting reservation to dictionary."""
        reservation = Reservation(
            "R001", "C001", "H001", "2024-12-01", "2024-12-03"
        )
        result = reservation.to_dict()

        expected_keys = {
            'reservation_id', 'customer_id', 'hotel_id',
            'check_in_date', 'check_out_date', 'status', 'created_at'
        }
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(result['reservation_id'], 'R001')
        self.assertEqual(result['status'], 'active')

    def test_reservation_from_dict(self):
        """Test creating reservation from dictionary."""
        created_at = datetime.now().isoformat()
        data = {
            'reservation_id': 'R001',
            'customer_id': 'C001',
            'hotel_id': 'H001',
            'check_in_date': '2024-12-01',
            'check_out_date': '2024-12-03',
            'status': 'active',
            'created_at': created_at
        }
        reservation = Reservation.from_dict(data)
        self.assertEqual(reservation.reservation_id, 'R001')
        self.assertEqual(reservation.status, ReservationStatus.ACTIVE)
        self.assertEqual(reservation.created_at, created_at)


if __name__ == '__main__':
    unittest.main()

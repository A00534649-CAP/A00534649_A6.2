"""
Models module for the Hotel Reservation System.
Contains the core data models: Hotel, Customer, and Reservation.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class ReservationStatus(Enum):
    """Enumeration for reservation statuses."""
    ACTIVE = "active"
    CANCELLED = "cancelled"


@dataclass
class Hotel:
    """
    Hotel model representing a hotel in the reservation system.

    Attributes:
        hotel_id (str): Unique identifier for the hotel
        name (str): Name of the hotel
        location (str): Location/address of the hotel
        total_rooms (int): Total number of rooms in the hotel
        available_rooms (int): Number of currently available rooms
    """
    hotel_id: str
    name: str
    location: str
    total_rooms: int
    available_rooms: int

    def __post_init__(self):
        """Validate hotel data after initialization."""
        self.validate()

    def validate(self):
        """Validate hotel attributes."""
        if not self.hotel_id:
            raise ValueError("Hotel ID cannot be empty")
        if not self.name:
            raise ValueError("Hotel name cannot be empty")
        if not self.location:
            raise ValueError("Hotel location cannot be empty")
        if self.total_rooms <= 0:
            raise ValueError("Total rooms must be greater than 0")
        if self.available_rooms < 0:
            raise ValueError("Available rooms cannot be negative")
        if self.available_rooms > self.total_rooms:
            raise ValueError("Available rooms cannot exceed total rooms")

    def reserve_room(self) -> bool:
        """
        Reserve a room if available.

        Returns:
            bool: True if reservation successful, False otherwise
        """
        if self.available_rooms > 0:
            self.available_rooms -= 1
            return True
        return False

    def cancel_reservation(self) -> bool:
        """
        Cancel a reservation and free up a room.

        Returns:
            bool: True if cancellation successful, False otherwise
        """
        if self.available_rooms < self.total_rooms:
            self.available_rooms += 1
            return True
        return False

    def to_dict(self) -> dict:
        """Convert hotel to dictionary representation."""
        return {
            'hotel_id': self.hotel_id,
            'name': self.name,
            'location': self.location,
            'total_rooms': self.total_rooms,
            'available_rooms': self.available_rooms
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Hotel':
        """Create Hotel instance from dictionary."""
        return cls(
            hotel_id=data['hotel_id'],
            name=data['name'],
            location=data['location'],
            total_rooms=data['total_rooms'],
            available_rooms=data['available_rooms']
        )


@dataclass
class Customer:
    """
    Customer model representing a customer in the reservation system.

    Attributes:
        customer_id (str): Unique identifier for the customer
        name (str): Full name of the customer
        email (str): Email address of the customer
        phone (str): Phone number of the customer
    """
    customer_id: str
    name: str
    email: str
    phone: str

    def __post_init__(self):
        """Validate customer data after initialization."""
        self.validate()

    def validate(self):
        """Validate customer attributes."""
        if not self.customer_id:
            raise ValueError("Customer ID cannot be empty")
        if not self.name:
            raise ValueError("Customer name cannot be empty")
        if not self.email:
            raise ValueError("Customer email cannot be empty")
        if not self._is_valid_email(self.email):
            raise ValueError("Invalid email format")
        if not self.phone:
            raise ValueError("Customer phone cannot be empty")

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def to_dict(self) -> dict:
        """Convert customer to dictionary representation."""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        """Create Customer instance from dictionary."""
        return cls(
            customer_id=data['customer_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone']
        )


@dataclass
class Reservation:
    """
    Reservation model representing a hotel reservation.

    Attributes:
        reservation_id (str): Unique identifier for the reservation
        customer_id (str): ID of the customer making the reservation
        hotel_id (str): ID of the hotel being reserved
        check_in_date (str): Check-in date in YYYY-MM-DD format
        check_out_date (str): Check-out date in YYYY-MM-DD format
        status (ReservationStatus): Status of the reservation
        created_at (str): Timestamp when reservation was created
    """
    reservation_id: str
    customer_id: str
    hotel_id: str
    check_in_date: str
    check_out_date: str
    status: ReservationStatus = ReservationStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate reservation data after initialization."""
        self.validate()

    def validate(self):
        """Validate reservation attributes."""
        if not self.reservation_id:
            raise ValueError("Reservation ID cannot be empty")
        if not self.customer_id:
            raise ValueError("Customer ID cannot be empty")
        if not self.hotel_id:
            raise ValueError("Hotel ID cannot be empty")
        if not self.check_in_date:
            raise ValueError("Check-in date cannot be empty")
        if not self.check_out_date:
            raise ValueError("Check-out date cannot be empty")

        # Validate date format
        try:
            check_in = datetime.fromisoformat(self.check_in_date)
            check_out = datetime.fromisoformat(self.check_out_date)
            if check_out <= check_in:
                raise ValueError("Check-out date must be after check-in date")
        except ValueError as e:
            if "Invalid isoformat string" in str(e):
                raise ValueError("Invalid date format. Use YYYY-MM-DD") from e
            raise

    def cancel(self):
        """Cancel the reservation."""
        self.status = ReservationStatus.CANCELLED

    def is_active(self) -> bool:
        """Check if reservation is active."""
        return self.status == ReservationStatus.ACTIVE

    def to_dict(self) -> dict:
        """Convert reservation to dictionary representation."""
        return {
            'reservation_id': self.reservation_id,
            'customer_id': self.customer_id,
            'hotel_id': self.hotel_id,
            'check_in_date': self.check_in_date,
            'check_out_date': self.check_out_date,
            'status': self.status.value,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Reservation':
        """Create Reservation instance from dictionary."""
        return cls(
            reservation_id=data['reservation_id'],
            customer_id=data['customer_id'],
            hotel_id=data['hotel_id'],
            check_in_date=data['check_in_date'],
            check_out_date=data['check_out_date'],
            status=ReservationStatus(data['status']),
            created_at=data.get('created_at', datetime.now().isoformat())
        )

"""
Reservation service module for the Hotel Reservation System.
Provides business logic for reservation management operations.
"""
from typing import List, Optional
from datetime import datetime
from src.models import Reservation, ReservationStatus
from src.storage import JSONStorage, StorageError
from src.hotel_service import HotelService, HotelServiceError
from src.customer_service import CustomerService, CustomerServiceError


class ReservationServiceError(Exception):
    """Custom exception for reservation service errors."""


class ReservationService:
    """
    Service class for reservation management operations.
    Handles business logic for reservation CRUD operations.
    """

    def __init__(self, storage: JSONStorage):
        """
        Initialize reservation service with storage backend.

        Args:
            storage (JSONStorage): Storage instance for data persistence
        """
        self.storage = storage
        self.hotel_service = HotelService(storage)
        self.customer_service = CustomerService(storage)

    def create_reservation(self, reservation_data: dict) -> Reservation:
        """
        Create a new reservation.

        Args:
            reservation_data (dict): Dictionary containing reservation information
                with keys:
                - reservation_id (str): Unique identifier for the reservation
                - customer_id (str): ID of the customer making the reservation
                - hotel_id (str): ID of the hotel being reserved
                - check_in_date (str): Check-in date in YYYY-MM-DD format
                - check_out_date (str): Check-out date in YYYY-MM-DD format

        Returns:
            Reservation: Created reservation instance

        Raises:
            ReservationServiceError: If reservation creation fails
        """
        try:
            # Extract data
            reservation_id = reservation_data['reservation_id']
            customer_id = reservation_data['customer_id']
            hotel_id = reservation_data['hotel_id']
            check_in_date = reservation_data['check_in_date']
            check_out_date = reservation_data['check_out_date']

            # Check if reservation already exists
            existing_reservation = self.storage.find_reservation_by_id(
                reservation_id
            )
            if existing_reservation:
                raise ReservationServiceError(
                    f"Reservation with ID {reservation_id} already exists"
                )

            # Verify customer exists
            customer = self.customer_service.get_customer(customer_id)
            if not customer:
                raise ReservationServiceError(
                    f"Customer with ID {customer_id} not found"
                )

            # Verify hotel exists and has availability
            hotel = self.hotel_service.get_hotel(hotel_id)
            if not hotel:
                raise ReservationServiceError(
                    f"Hotel with ID {hotel_id} not found"
                )

            if hotel.available_rooms <= 0:
                raise ReservationServiceError(
                    f"No rooms available at hotel {hotel_id}"
                )

            # Create reservation instance (validation happens in __post_init__)
            reservation = Reservation(
                reservation_id=reservation_id,
                customer_id=customer_id,
                hotel_id=hotel_id,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                status=ReservationStatus.ACTIVE
            )

            # Reserve room in hotel
            if not self.hotel_service.reserve_room(hotel_id):
                raise ReservationServiceError(
                    f"Failed to reserve room at hotel {hotel_id}"
                )

            # Save reservation
            self.storage.save_reservation(reservation)
            return reservation

        except ValueError as e:
            raise ReservationServiceError(f"Invalid reservation data: {e}") from e
        except (StorageError, HotelServiceError, CustomerServiceError) as e:
            raise ReservationServiceError(f"Service error: {e}") from e

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """
        Retrieve a reservation by ID.

        Args:
            reservation_id (str): Reservation ID to search for

        Returns:
            Optional[Reservation]: Reservation instance if found, None otherwise

        Raises:
            ReservationServiceError: If storage error occurs
        """
        try:
            return self.storage.find_reservation_by_id(reservation_id)
        except StorageError as e:
            raise ReservationServiceError(f"Storage error: {e}") from e

    def get_all_reservations(self) -> List[Reservation]:
        """
        Retrieve all reservations.

        Returns:
            List[Reservation]: List of all reservations

        Raises:
            ReservationServiceError: If storage error occurs
        """
        try:
            return self.storage.load_reservations()
        except StorageError as e:
            raise ReservationServiceError(f"Storage error: {e}") from e

    def cancel_reservation(self, reservation_id: str) -> bool:
        """
        Cancel a reservation.

        Args:
            reservation_id (str): ID of reservation to cancel

        Returns:
            bool: True if reservation was cancelled, False if not found or
                  already cancelled

        Raises:
            ReservationServiceError: If storage or hotel service error occurs
        """
        try:
            reservation = self.storage.find_reservation_by_id(reservation_id)
            if not reservation:
                raise ReservationServiceError(
                    f"Reservation with ID {reservation_id} not found"
                )

            if not reservation.is_active():
                return False  # Already cancelled

            # Cancel the reservation
            reservation.cancel()

            # Free up the hotel room
            if not self.hotel_service.cancel_reservation_room(reservation.hotel_id):
                # Log warning but don't fail the cancellation
                print(f"Warning: Could not free room for hotel {reservation.hotel_id}")

            # Save updated reservation
            self.storage.save_reservation(reservation)
            return True

        except (StorageError, HotelServiceError) as e:
            raise ReservationServiceError(f"Service error: {e}") from e

    def display_reservation_info(self, reservation_id: str) -> str:
        """
        Display formatted reservation information.

        Args:
            reservation_id (str): ID of reservation to display

        Returns:
            str: Formatted reservation information

        Raises:
            ReservationServiceError: If reservation not found or service error occurs
        """
        try:
            reservation = self.storage.find_reservation_by_id(reservation_id)
            if not reservation:
                raise ReservationServiceError(
                    f"Reservation with ID {reservation_id} not found"
                )

            # Get customer and hotel information
            customer = self.customer_service.get_customer(reservation.customer_id)
            hotel = self.hotel_service.get_hotel(reservation.hotel_id)

            customer_name = customer.name if customer else "Unknown Customer"
            hotel_name = hotel.name if hotel else "Unknown Hotel"

            # Calculate stay duration
            check_in = datetime.fromisoformat(reservation.check_in_date)
            check_out = datetime.fromisoformat(reservation.check_out_date)
            stay_duration = (check_out - check_in).days

            return (
                f"Reservation Information:\n"
                f"ID: {reservation.reservation_id}\n"
                f"Customer: {customer_name} (ID: {reservation.customer_id})\n"
                f"Hotel: {hotel_name} (ID: {reservation.hotel_id})\n"
                f"Check-in Date: {reservation.check_in_date}\n"
                f"Check-out Date: {reservation.check_out_date}\n"
                f"Stay Duration: {stay_duration} nights\n"
                f"Status: {reservation.status.value.title()}\n"
                f"Created: {reservation.created_at}"
            )

        except (StorageError, HotelServiceError, CustomerServiceError) as e:
            raise ReservationServiceError(f"Service error: {e}") from e

    def get_reservations_by_customer(self, customer_id: str) -> List[Reservation]:
        """
        Get all reservations for a specific customer.

        Args:
            customer_id (str): Customer ID to get reservations for

        Returns:
            List[Reservation]: List of reservations for the customer

        Raises:
            ReservationServiceError: If storage error occurs
        """
        try:
            return self.storage.get_reservations_by_customer(customer_id)
        except StorageError as e:
            raise ReservationServiceError(f"Storage error: {e}") from e

    def get_reservations_by_hotel(self, hotel_id: str) -> List[Reservation]:
        """
        Get all reservations for a specific hotel.

        Args:
            hotel_id (str): Hotel ID to get reservations for

        Returns:
            List[Reservation]: List of reservations for the hotel

        Raises:
            ReservationServiceError: If storage error occurs
        """
        try:
            return self.storage.get_reservations_by_hotel(hotel_id)
        except StorageError as e:
            raise ReservationServiceError(f"Storage error: {e}") from e

    def get_active_reservations(self) -> List[Reservation]:
        """
        Get all active reservations.

        Returns:
            List[Reservation]: List of active reservations

        Raises:
            ReservationServiceError: If storage error occurs
        """
        try:
            all_reservations = self.storage.load_reservations()
            return [r for r in all_reservations if r.is_active()]
        except StorageError as e:
            raise ReservationServiceError(f"Storage error: {e}") from e

    def is_reservation_valid(self, customer_id: str, hotel_id: str,
                             check_in_date: str, check_out_date: str) -> tuple:
        """
        Validate if a reservation can be created.

        Args:
            customer_id (str): Customer ID
            hotel_id (str): Hotel ID
            check_in_date (str): Check-in date
            check_out_date (str): Check-out date

        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        try:
            # Validate customer
            error_msg = self._validate_customer(customer_id)
            if error_msg:
                return False, error_msg

            # Validate hotel
            _, error_msg = self._validate_hotel_availability(hotel_id)
            if error_msg:
                return False, error_msg

            # Validate dates
            error_msg = self._validate_reservation_dates(check_in_date, check_out_date)
            if error_msg:
                return False, error_msg

            return True, "Reservation is valid"

        except (HotelServiceError, CustomerServiceError) as e:
            return False, str(e)

    def _validate_customer(self, customer_id: str) -> Optional[str]:
        """Validate customer exists."""
        customer = self.customer_service.get_customer(customer_id)
        if not customer:
            return f"Customer with ID {customer_id} not found"
        return None

    def _validate_hotel_availability(self, hotel_id: str) -> tuple:
        """Validate hotel exists and has availability."""
        hotel = self.hotel_service.get_hotel(hotel_id)
        if not hotel:
            return None, f"Hotel with ID {hotel_id} not found"
        if hotel.available_rooms <= 0:
            return None, f"No rooms available at hotel {hotel_id}"
        return hotel, None

    def _validate_reservation_dates(
        self, check_in_date: str, check_out_date: str
    ) -> Optional[str]:
        """Validate reservation dates."""
        try:
            check_in = datetime.fromisoformat(check_in_date)
            check_out = datetime.fromisoformat(check_out_date)

            if check_out <= check_in:
                return "Check-out date must be after check-in date"

            if check_in.date() < datetime.now().date():
                return "Check-in date cannot be in the past"

        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD"

        return None

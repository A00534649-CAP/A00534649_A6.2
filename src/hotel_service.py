"""
Hotel service module for the Hotel Reservation System.
Provides business logic for hotel management operations.
"""
from typing import List, Optional
from src.models import Hotel
from src.storage import JSONStorage, StorageError


class HotelServiceError(Exception):
    """Custom exception for hotel service errors."""


class HotelService:
    """
    Service class for hotel management operations.
    Handles business logic for hotel CRUD operations.
    """

    def __init__(self, storage: JSONStorage):
        """
        Initialize hotel service with storage backend.

        Args:
            storage (JSONStorage): Storage instance for data persistence
        """
        self.storage = storage

    def create_hotel(self, hotel_data: dict) -> Hotel:
        """
        Create a new hotel.

        Args:
            hotel_data (dict): Dictionary containing hotel information with keys:
                - hotel_id (str): Unique identifier for the hotel
                - name (str): Name of the hotel
                - location (str): Location of the hotel
                - total_rooms (int): Total number of rooms
                - available_rooms (int): Number of available rooms

        Returns:
            Hotel: Created hotel instance

        Raises:
            HotelServiceError: If hotel creation fails
        """
        try:
            # Check if hotel already exists
            hotel_id = hotel_data['hotel_id']
            existing_hotel = self.storage.find_hotel_by_id(hotel_id)
            if existing_hotel:
                raise HotelServiceError(f"Hotel with ID {hotel_id} already exists")

            # Create hotel instance (validation happens in __post_init__)
            hotel = Hotel(
                hotel_id=hotel_data['hotel_id'],
                name=hotel_data['name'],
                location=hotel_data['location'],
                total_rooms=hotel_data['total_rooms'],
                available_rooms=hotel_data['available_rooms']
            )

            # Save to storage
            self.storage.save_hotel(hotel)
            return hotel

        except ValueError as e:
            raise HotelServiceError(f"Invalid hotel data: {e}") from e
        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

    def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        """
        Retrieve a hotel by ID.

        Args:
            hotel_id (str): Hotel ID to search for

        Returns:
            Optional[Hotel]: Hotel instance if found, None otherwise

        Raises:
            HotelServiceError: If storage error occurs
        """
        try:
            return self.storage.find_hotel_by_id(hotel_id)
        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

    def get_all_hotels(self) -> List[Hotel]:
        """
        Retrieve all hotels.

        Returns:
            List[Hotel]: List of all hotels

        Raises:
            HotelServiceError: If storage error occurs
        """
        try:
            return self.storage.load_hotels()
        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

    def update_hotel(self, hotel_id: str, update_data: dict) -> Hotel:
        """
        Update hotel information.

        Args:
            hotel_id (str): ID of hotel to update
            update_data (dict): Dictionary containing fields to update

        Returns:
            Hotel: Updated hotel instance

        Raises:
            HotelServiceError: If hotel not found or update fails
        """
        try:
            hotel = self.storage.find_hotel_by_id(hotel_id)
            if not hotel:
                raise HotelServiceError(f"Hotel with ID {hotel_id} not found")

            # Update fields if provided
            if 'name' in update_data:
                hotel.name = update_data['name']
            if 'location' in update_data:
                hotel.location = update_data['location']
            if 'total_rooms' in update_data:
                hotel.total_rooms = update_data['total_rooms']
            if 'available_rooms' in update_data:
                hotel.available_rooms = update_data['available_rooms']

            # Re-validate hotel data
            hotel.validate()

            # Save updated hotel
            self.storage.save_hotel(hotel)
            return hotel

        except ValueError as e:
            raise HotelServiceError(f"Invalid hotel data: {e}") from e
        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

    def delete_hotel(self, hotel_id: str) -> bool:
        """
        Delete a hotel.

        Args:
            hotel_id (str): ID of hotel to delete

        Returns:
            bool: True if hotel was deleted, False if not found

        Raises:
            HotelServiceError: If storage error occurs
        """
        try:
            # Check if hotel has active reservations
            reservations = self.storage.get_reservations_by_hotel(hotel_id)
            active_reservations = [r for r in reservations if r.is_active()]

            if active_reservations:
                raise HotelServiceError(
                    f"Cannot delete hotel {hotel_id}: has active reservations"
                )

            return self.storage.delete_hotel(hotel_id)

        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

    def reserve_room(self, hotel_id: str) -> bool:
        """
        Reserve a room in the specified hotel.

        Args:
            hotel_id (str): ID of hotel to reserve room in

        Returns:
            bool: True if reservation successful, False if no rooms available

        Raises:
            HotelServiceError: If hotel not found or storage error occurs
        """
        try:
            hotel = self.storage.find_hotel_by_id(hotel_id)
            if not hotel:
                raise HotelServiceError(f"Hotel with ID {hotel_id} not found")

            if hotel.reserve_room():
                self.storage.save_hotel(hotel)
                return True
            return False

        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

    def cancel_reservation_room(self, hotel_id: str) -> bool:
        """
        Cancel a room reservation and free up the room.

        Args:
            hotel_id (str): ID of hotel to free room in

        Returns:
            bool: True if cancellation successful

        Raises:
            HotelServiceError: If hotel not found or storage error occurs
        """
        try:
            hotel = self.storage.find_hotel_by_id(hotel_id)
            if not hotel:
                raise HotelServiceError(f"Hotel with ID {hotel_id} not found")

            if hotel.cancel_reservation():
                self.storage.save_hotel(hotel)
                return True
            return False

        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

    def display_hotel_info(self, hotel_id: str) -> str:
        """
        Display formatted hotel information.

        Args:
            hotel_id (str): ID of hotel to display

        Returns:
            str: Formatted hotel information

        Raises:
            HotelServiceError: If hotel not found or storage error occurs
        """
        try:
            hotel = self.storage.find_hotel_by_id(hotel_id)
            if not hotel:
                raise HotelServiceError(f"Hotel with ID {hotel_id} not found")

            occupancy_rate = ((hotel.total_rooms - hotel.available_rooms) /
                              hotel.total_rooms * 100)
            return (
                f"Hotel Information:\n"
                f"ID: {hotel.hotel_id}\n"
                f"Name: {hotel.name}\n"
                f"Location: {hotel.location}\n"
                f"Total Rooms: {hotel.total_rooms}\n"
                f"Available Rooms: {hotel.available_rooms}\n"
                f"Occupancy Rate: {occupancy_rate:.1f}%"
            )

        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

    def get_hotel_availability(self, hotel_id: str) -> Optional[int]:
        """
        Get available room count for a hotel.

        Args:
            hotel_id (str): ID of hotel to check

        Returns:
            Optional[int]: Number of available rooms, None if hotel not found

        Raises:
            HotelServiceError: If storage error occurs
        """
        try:
            hotel = self.storage.find_hotel_by_id(hotel_id)
            return hotel.available_rooms if hotel else None

        except StorageError as e:
            raise HotelServiceError(f"Storage error: {e}") from e

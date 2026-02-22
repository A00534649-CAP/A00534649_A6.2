"""
Storage module for the Hotel Reservation System.
Handles JSON file operations for persistent data storage.
"""
import json
import os
from typing import List, Dict, Any, Optional
from src.models import Hotel, Customer, Reservation


class StorageError(Exception):
    """Custom exception for storage-related errors."""


class JSONStorage:
    """
    JSON storage handler for the reservation system.
    Manages persistent storage of hotels, customers, and reservations.
    """

    def __init__(self, data_directory: str = "data"):
        """
        Initialize JSON storage.

        Args:
            data_directory (str): Directory to store JSON files
        """
        self.data_directory = data_directory
        self.hotels_file = os.path.join(data_directory, "hotels.json")
        self.customers_file = os.path.join(data_directory, "customers.json")
        self.reservations_file = os.path.join(data_directory, "reservations.json")
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)

    def _read_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Read and parse JSON file.

        Args:
            file_path (str): Path to JSON file

        Returns:
            List[Dict]: List of dictionaries from JSON file

        Raises:
            StorageError: If file cannot be read or parsed
        """
        try:
            if not os.path.exists(file_path):
                return []

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    return []
                return json.loads(content)

        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid JSON format in {file_path}: {e}") from e
        except IOError as e:
            raise StorageError(f"Error reading file {file_path}: {e}") from e

    def _write_json_file(self, file_path: str, data: List[Dict[str, Any]]):
        """
        Write data to JSON file.

        Args:
            file_path (str): Path to JSON file
            data (List[Dict]): Data to write

        Raises:
            StorageError: If file cannot be written
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except IOError as e:
            raise StorageError(f"Error writing to file {file_path}: {e}") from e

    # Hotel storage methods
    def save_hotels(self, hotels: List[Hotel]):
        """Save list of hotels to JSON file."""
        data = [hotel.to_dict() for hotel in hotels]
        self._write_json_file(self.hotels_file, data)

    def load_hotels(self) -> List[Hotel]:
        """Load hotels from JSON file."""
        try:
            data = self._read_json_file(self.hotels_file)
            return [Hotel.from_dict(item) for item in data]
        except (ValueError, KeyError) as e:
            raise StorageError(f"Invalid hotel data format: {e}") from e

    def find_hotel_by_id(self, hotel_id: str) -> Optional[Hotel]:
        """Find hotel by ID."""
        hotels = self.load_hotels()
        for hotel in hotels:
            if hotel.hotel_id == hotel_id:
                return hotel
        return None

    def save_hotel(self, hotel: Hotel):
        """Save or update a single hotel."""
        hotels = self.load_hotels()

        # Update existing hotel or add new one
        for i, existing_hotel in enumerate(hotels):
            if existing_hotel.hotel_id == hotel.hotel_id:
                hotels[i] = hotel
                break
        else:
            hotels.append(hotel)

        self.save_hotels(hotels)

    def delete_hotel(self, hotel_id: str) -> bool:
        """Delete hotel by ID. Returns True if deleted, False if not found."""
        hotels = self.load_hotels()
        original_count = len(hotels)
        hotels = [h for h in hotels if h.hotel_id != hotel_id]

        if len(hotels) < original_count:
            self.save_hotels(hotels)
            return True
        return False

    # Customer storage methods
    def save_customers(self, customers: List[Customer]):
        """Save list of customers to JSON file."""
        data = [customer.to_dict() for customer in customers]
        self._write_json_file(self.customers_file, data)

    def load_customers(self) -> List[Customer]:
        """Load customers from JSON file."""
        try:
            data = self._read_json_file(self.customers_file)
            return [Customer.from_dict(item) for item in data]
        except (ValueError, KeyError) as e:
            raise StorageError(f"Invalid customer data format: {e}") from e

    def find_customer_by_id(self, customer_id: str) -> Optional[Customer]:
        """Find customer by ID."""
        customers = self.load_customers()
        for customer in customers:
            if customer.customer_id == customer_id:
                return customer
        return None

    def save_customer(self, customer: Customer):
        """Save or update a single customer."""
        customers = self.load_customers()

        # Update existing customer or add new one
        for i, existing_customer in enumerate(customers):
            if existing_customer.customer_id == customer.customer_id:
                customers[i] = customer
                break
        else:
            customers.append(customer)

        self.save_customers(customers)

    def delete_customer(self, customer_id: str) -> bool:
        """Delete customer by ID. Returns True if deleted, False if not found."""
        customers = self.load_customers()
        original_count = len(customers)
        customers = [c for c in customers if c.customer_id != customer_id]

        if len(customers) < original_count:
            self.save_customers(customers)
            return True
        return False

    # Reservation storage methods
    def save_reservations(self, reservations: List[Reservation]):
        """Save list of reservations to JSON file."""
        data = [reservation.to_dict() for reservation in reservations]
        self._write_json_file(self.reservations_file, data)

    def load_reservations(self) -> List[Reservation]:
        """Load reservations from JSON file."""
        try:
            data = self._read_json_file(self.reservations_file)
            return [Reservation.from_dict(item) for item in data]
        except (ValueError, KeyError) as e:
            raise StorageError(f"Invalid reservation data format: {e}") from e

    def find_reservation_by_id(self, reservation_id: str) -> Optional[Reservation]:
        """Find reservation by ID."""
        reservations = self.load_reservations()
        for reservation in reservations:
            if reservation.reservation_id == reservation_id:
                return reservation
        return None

    def save_reservation(self, reservation: Reservation):
        """Save or update a single reservation."""
        reservations = self.load_reservations()

        # Update existing reservation or add new one
        for i, existing_reservation in enumerate(reservations):
            if existing_reservation.reservation_id == reservation.reservation_id:
                reservations[i] = reservation
                break
        else:
            reservations.append(reservation)

        self.save_reservations(reservations)

    def delete_reservation(self, reservation_id: str) -> bool:
        """Delete reservation by ID. Returns True if deleted, False if not found."""
        reservations = self.load_reservations()
        original_count = len(reservations)
        reservations = [r for r in reservations if r.reservation_id != reservation_id]

        if len(reservations) < original_count:
            self.save_reservations(reservations)
            return True
        return False

    def get_reservations_by_customer(self, customer_id: str) -> List[Reservation]:
        """Get all reservations for a specific customer."""
        reservations = self.load_reservations()
        return [r for r in reservations if r.customer_id == customer_id]

    def get_reservations_by_hotel(self, hotel_id: str) -> List[Reservation]:
        """Get all reservations for a specific hotel."""
        reservations = self.load_reservations()
        return [r for r in reservations if r.hotel_id == hotel_id]

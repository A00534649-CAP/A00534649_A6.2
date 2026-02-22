"""
Customer service module for the Hotel Reservation System.
Provides business logic for customer management operations.
"""
from typing import List, Optional
from src.models import Customer
from src.storage import JSONStorage, StorageError


class CustomerServiceError(Exception):
    """Custom exception for customer service errors."""


class CustomerService:
    """
    Service class for customer management operations.
    Handles business logic for customer CRUD operations.
    """

    def __init__(self, storage: JSONStorage):
        """
        Initialize customer service with storage backend.

        Args:
            storage (JSONStorage): Storage instance for data persistence
        """
        self.storage = storage

    def create_customer(self, customer_id: str, name: str,
                        email: str, phone: str) -> Customer:
        """
        Create a new customer.

        Args:
            customer_id (str): Unique identifier for the customer
            name (str): Customer's full name
            email (str): Customer's email address
            phone (str): Customer's phone number

        Returns:
            Customer: Created customer instance

        Raises:
            CustomerServiceError: If customer creation fails
        """
        try:
            # Check if customer already exists
            existing_customer = self.storage.find_customer_by_id(customer_id)
            if existing_customer:
                raise CustomerServiceError(
                    f"Customer with ID {customer_id} already exists"
                )

            # Check for duplicate email
            customers = self.storage.load_customers()
            for customer in customers:
                if customer.email.lower() == email.lower():
                    raise CustomerServiceError(
                        f"Customer with email {email} already exists"
                    )

            # Create customer instance (validation happens in __post_init__)
            customer = Customer(
                customer_id=customer_id,
                name=name,
                email=email,
                phone=phone
            )

            # Save to storage
            self.storage.save_customer(customer)
            return customer

        except ValueError as e:
            raise CustomerServiceError(f"Invalid customer data: {e}") from e
        except StorageError as e:
            raise CustomerServiceError(f"Storage error: {e}") from e

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """
        Retrieve a customer by ID.

        Args:
            customer_id (str): Customer ID to search for

        Returns:
            Optional[Customer]: Customer instance if found, None otherwise

        Raises:
            CustomerServiceError: If storage error occurs
        """
        try:
            return self.storage.find_customer_by_id(customer_id)
        except StorageError as e:
            raise CustomerServiceError(f"Storage error: {e}") from e

    def get_all_customers(self) -> List[Customer]:
        """
        Retrieve all customers.

        Returns:
            List[Customer]: List of all customers

        Raises:
            CustomerServiceError: If storage error occurs
        """
        try:
            return self.storage.load_customers()
        except StorageError as e:
            raise CustomerServiceError(f"Storage error: {e}") from e

    def update_customer(self, customer_id: str, name: Optional[str] = None,
                        email: Optional[str] = None,
                        phone: Optional[str] = None) -> Customer:
        """
        Update customer information.

        Args:
            customer_id (str): ID of customer to update
            name (Optional[str]): New customer name
            email (Optional[str]): New customer email
            phone (Optional[str]): New customer phone

        Returns:
            Customer: Updated customer instance

        Raises:
            CustomerServiceError: If customer not found or update fails
        """
        try:
            customer = self.storage.find_customer_by_id(customer_id)
            if not customer:
                raise CustomerServiceError(
                    f"Customer with ID {customer_id} not found"
                )

            # Check for duplicate email if email is being updated
            if email and email.lower() != customer.email.lower():
                customers = self.storage.load_customers()
                for existing_customer in customers:
                    if (existing_customer.customer_id != customer_id and
                            existing_customer.email.lower() == email.lower()):
                        raise CustomerServiceError(
                            f"Customer with email {email} already exists"
                        )

            # Update fields if provided
            if name is not None:
                customer.name = name
            if email is not None:
                customer.email = email
            if phone is not None:
                customer.phone = phone

            # Re-validate customer data
            customer.validate()

            # Save updated customer
            self.storage.save_customer(customer)
            return customer

        except ValueError as e:
            raise CustomerServiceError(f"Invalid customer data: {e}") from e
        except StorageError as e:
            raise CustomerServiceError(f"Storage error: {e}") from e

    def delete_customer(self, customer_id: str) -> bool:
        """
        Delete a customer.

        Args:
            customer_id (str): ID of customer to delete

        Returns:
            bool: True if customer was deleted, False if not found

        Raises:
            CustomerServiceError: If customer has active reservations or storage error
        """
        try:
            # Check if customer has active reservations
            reservations = self.storage.get_reservations_by_customer(customer_id)
            active_reservations = [r for r in reservations if r.is_active()]

            if active_reservations:
                raise CustomerServiceError(
                    f"Cannot delete customer {customer_id}: has active reservations"
                )

            return self.storage.delete_customer(customer_id)

        except StorageError as e:
            raise CustomerServiceError(f"Storage error: {e}") from e

    def display_customer_info(self, customer_id: str) -> str:
        """
        Display formatted customer information.

        Args:
            customer_id (str): ID of customer to display

        Returns:
            str: Formatted customer information

        Raises:
            CustomerServiceError: If customer not found or storage error occurs
        """
        try:
            customer = self.storage.find_customer_by_id(customer_id)
            if not customer:
                raise CustomerServiceError(
                    f"Customer with ID {customer_id} not found"
                )

            # Get customer's reservations
            reservations = self.storage.get_reservations_by_customer(customer_id)
            active_reservations = [r for r in reservations if r.is_active()]

            return (
                f"Customer Information:\n"
                f"ID: {customer.customer_id}\n"
                f"Name: {customer.name}\n"
                f"Email: {customer.email}\n"
                f"Phone: {customer.phone}\n"
                f"Total Reservations: {len(reservations)}\n"
                f"Active Reservations: {len(active_reservations)}"
            )

        except StorageError as e:
            raise CustomerServiceError(f"Storage error: {e}") from e

    def find_customer_by_email(self, email: str) -> Optional[Customer]:
        """
        Find customer by email address.

        Args:
            email (str): Email address to search for

        Returns:
            Optional[Customer]: Customer instance if found, None otherwise

        Raises:
            CustomerServiceError: If storage error occurs
        """
        try:
            customers = self.storage.load_customers()
            for customer in customers:
                if customer.email.lower() == email.lower():
                    return customer
            return None

        except StorageError as e:
            raise CustomerServiceError(f"Storage error: {e}") from e

    def get_customer_reservations(self, customer_id: str) -> List:
        """
        Get all reservations for a specific customer.

        Args:
            customer_id (str): Customer ID to get reservations for

        Returns:
            List: List of reservations for the customer

        Raises:
            CustomerServiceError: If storage error occurs
        """
        try:
            # Verify customer exists
            customer = self.storage.find_customer_by_id(customer_id)
            if not customer:
                raise CustomerServiceError(
                    f"Customer with ID {customer_id} not found"
                )

            return self.storage.get_reservations_by_customer(customer_id)

        except StorageError as e:
            raise CustomerServiceError(f"Storage error: {e}") from e

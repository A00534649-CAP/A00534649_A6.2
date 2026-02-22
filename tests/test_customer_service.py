"""
Unit tests for the customer_service module.
Tests CustomerService class business logic operations.
"""
import unittest
import tempfile
import shutil
from unittest.mock import patch
from src.customer_service import CustomerService, CustomerServiceError
from src.storage import JSONStorage, StorageError
from src.models import Reservation


class TestCustomerService(unittest.TestCase):
    """Test cases for the CustomerService class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = JSONStorage(self.test_dir)
        self.customer_service = CustomerService(self.storage)

    def tearDown(self):
        """Clean up after each test method."""
        if self.test_dir:
            shutil.rmtree(self.test_dir)

    # Customer creation tests
    def test_create_customer_success(self):
        """Test successful customer creation."""
        customer = self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        self.assertEqual(customer.customer_id, "C001")
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.email, "john@example.com")
        self.assertEqual(customer.phone, "123-456-7890")

    def test_create_customer_duplicate_id(self):
        """Test creating customer with duplicate ID raises error."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.create_customer(
                "C001", "Jane Doe", "jane@example.com", "987-654-3210"
            )

        self.assertIn("Customer with ID C001 already exists", str(context.exception))

    def test_create_customer_duplicate_email(self):
        """Test creating customer with duplicate email raises error."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.create_customer(
                "C002", "Jane Doe", "john@example.com", "987-654-3210"
            )

        self.assertIn("Customer with email john@example.com already exists",
                      str(context.exception))

    def test_create_customer_duplicate_email_case_insensitive(self):
        """Test creating customer with duplicate email (case insensitive) raises error."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.create_customer(
                "C002", "Jane Doe", "JOHN@EXAMPLE.COM", "987-654-3210"
            )

        self.assertIn("Customer with email JOHN@EXAMPLE.COM already exists", str(context.exception))

    def test_create_customer_invalid_data_empty_id(self):
        """Test creating customer with empty ID raises error."""
        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.create_customer(
                "", "John Doe", "john@example.com", "123-456-7890"
            )

        self.assertIn("Invalid customer data", str(context.exception))

    def test_create_customer_invalid_email_format(self):
        """Test creating customer with invalid email format raises error."""
        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.create_customer(
                "C001", "John Doe", "invalid-email", "123-456-7890"
            )

        self.assertIn("Invalid customer data", str(context.exception))

    def test_create_customer_empty_name(self):
        """Test creating customer with empty name raises error."""
        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.create_customer(
                "C001", "", "john@example.com", "123-456-7890"
            )

        self.assertIn("Invalid customer data", str(context.exception))

    def test_create_customer_empty_phone(self):
        """Test creating customer with empty phone raises error."""
        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.create_customer(
                "C001", "John Doe", "john@example.com", ""
            )

        self.assertIn("Invalid customer data", str(context.exception))

    # Customer retrieval tests
    def test_get_customer_exists(self):
        """Test getting customer that exists."""
        created_customer = self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )
        retrieved_customer = self.customer_service.get_customer("C001")

        self.assertIsNotNone(retrieved_customer)
        self.assertEqual(retrieved_customer.customer_id, created_customer.customer_id)
        self.assertEqual(retrieved_customer.name, created_customer.name)

    def test_get_customer_not_exists(self):
        """Test getting customer that doesn't exist."""
        retrieved_customer = self.customer_service.get_customer("C999")
        self.assertIsNone(retrieved_customer)

    def test_get_all_customers_empty(self):
        """Test getting all customers when none exist."""
        customers = self.customer_service.get_all_customers()
        self.assertEqual(customers, [])

    def test_get_all_customers_multiple(self):
        """Test getting all customers when multiple exist."""
        self.customer_service.create_customer("C001", "John", "john@test.com", "123")
        self.customer_service.create_customer("C002", "Jane", "jane@test.com", "456")

        customers = self.customer_service.get_all_customers()
        self.assertEqual(len(customers), 2)

        customer_ids = [c.customer_id for c in customers]
        self.assertIn("C001", customer_ids)
        self.assertIn("C002", customer_ids)

    # Customer update tests
    def test_update_customer_name(self):
        """Test updating customer name."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        updated_customer = self.customer_service.update_customer("C001", name="Jane Doe")
        self.assertEqual(updated_customer.name, "Jane Doe")
        self.assertEqual(updated_customer.email, "john@example.com")  # Unchanged

    def test_update_customer_email(self):
        """Test updating customer email."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        updated_customer = self.customer_service.update_customer(
            "C001", email="newemail@example.com"
        )
        self.assertEqual(updated_customer.email, "newemail@example.com")
        self.assertEqual(updated_customer.name, "John Doe")  # Unchanged

    def test_update_customer_all_fields(self):
        """Test updating all customer fields."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        updated_customer = self.customer_service.update_customer(
            "C001",
            name="Jane Smith",
            email="jane@example.com",
            phone="987-654-3210"
        )

        self.assertEqual(updated_customer.name, "Jane Smith")
        self.assertEqual(updated_customer.email, "jane@example.com")
        self.assertEqual(updated_customer.phone, "987-654-3210")

    def test_update_customer_not_exists(self):
        """Test updating customer that doesn't exist raises error."""
        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.update_customer("C999", name="New Name")

        self.assertIn("Customer with ID C999 not found", str(context.exception))

    def test_update_customer_duplicate_email(self):
        """Test updating customer with duplicate email raises error."""
        self.customer_service.create_customer("C001", "John", "john@test.com", "123")
        self.customer_service.create_customer("C002", "Jane", "jane@test.com", "456")

        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.update_customer("C001", email="jane@test.com")

        self.assertIn("Customer with email jane@test.com already exists", str(context.exception))

    def test_update_customer_same_email(self):
        """Test updating customer with same email succeeds."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        # Should succeed when updating with same email
        updated_customer = self.customer_service.update_customer(
            "C001", email="john@example.com", name="John Smith"
        )
        self.assertEqual(updated_customer.name, "John Smith")
        self.assertEqual(updated_customer.email, "john@example.com")

    def test_update_customer_invalid_data(self):
        """Test updating customer with invalid data raises error."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.update_customer("C001", email="invalid-email")

        self.assertIn("Invalid customer data", str(context.exception))

    # Customer deletion tests
    def test_delete_customer_success(self):
        """Test successful customer deletion."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        result = self.customer_service.delete_customer("C001")
        self.assertTrue(result)

        retrieved_customer = self.customer_service.get_customer("C001")
        self.assertIsNone(retrieved_customer)

    def test_delete_customer_not_exists(self):
        """Test deleting customer that doesn't exist."""
        result = self.customer_service.delete_customer("C999")
        self.assertFalse(result)

    def test_delete_customer_with_active_reservations(self):
        """Test deleting customer with active reservations raises error."""
        # Create customer
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        # Create active reservation
        reservation = Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03")
        self.storage.save_reservation(reservation)

        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.delete_customer("C001")

        self.assertIn("has active reservations", str(context.exception))

    def test_delete_customer_with_cancelled_reservations(self):
        """Test deleting customer with only cancelled reservations succeeds."""
        # Create customer
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        # Create cancelled reservation
        reservation = Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03")
        reservation.cancel()
        self.storage.save_reservation(reservation)

        result = self.customer_service.delete_customer("C001")
        self.assertTrue(result)

    # Display and utility tests
    def test_display_customer_info(self):
        """Test displaying customer information."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        info = self.customer_service.display_customer_info("C001")

        self.assertIn("Customer Information:", info)
        self.assertIn("ID: C001", info)
        self.assertIn("Name: John Doe", info)
        self.assertIn("Email: john@example.com", info)
        self.assertIn("Phone: 123-456-7890", info)
        self.assertIn("Total Reservations: 0", info)
        self.assertIn("Active Reservations: 0", info)

    def test_display_customer_info_with_reservations(self):
        """Test displaying customer info with reservations."""
        # Create customer
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        # Create reservations
        active_reservation = Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03")
        cancelled_reservation = Reservation("R002", "C001", "H002", "2024-12-05", "2024-12-07")
        cancelled_reservation.cancel()

        self.storage.save_reservation(active_reservation)
        self.storage.save_reservation(cancelled_reservation)

        info = self.customer_service.display_customer_info("C001")

        self.assertIn("Total Reservations: 2", info)
        self.assertIn("Active Reservations: 1", info)

    def test_display_customer_info_not_exists(self):
        """Test displaying info for non-existent customer raises error."""
        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.display_customer_info("C999")

        self.assertIn("Customer with ID C999 not found", str(context.exception))

    def test_find_customer_by_email(self):
        """Test finding customer by email."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        found_customer = self.customer_service.find_customer_by_email("john@example.com")
        self.assertIsNotNone(found_customer)
        self.assertEqual(found_customer.customer_id, "C001")

    def test_find_customer_by_email_case_insensitive(self):
        """Test finding customer by email (case insensitive)."""
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        found_customer = self.customer_service.find_customer_by_email("JOHN@EXAMPLE.COM")
        self.assertIsNotNone(found_customer)
        self.assertEqual(found_customer.customer_id, "C001")

    def test_find_customer_by_email_not_exists(self):
        """Test finding customer by email when it doesn't exist."""
        found_customer = self.customer_service.find_customer_by_email("nonexistent@example.com")
        self.assertIsNone(found_customer)

    def test_get_customer_reservations(self):
        """Test getting customer reservations."""
        # Create customer
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )

        # Create reservations
        reservation1 = Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03")
        reservation2 = Reservation("R002", "C001", "H002", "2024-12-05", "2024-12-07")

        self.storage.save_reservation(reservation1)
        self.storage.save_reservation(reservation2)

        reservations = self.customer_service.get_customer_reservations("C001")
        self.assertEqual(len(reservations), 2)

    def test_get_customer_reservations_not_exists(self):
        """Test getting reservations for non-existent customer raises error."""
        with self.assertRaises(CustomerServiceError) as context:
            self.customer_service.get_customer_reservations("C999")

        self.assertIn("Customer with ID C999 not found", str(context.exception))

    def test_create_customer_storage_error(self):
        """Test create customer with storage error."""
        with patch.object(self.storage, 'save_customer', side_effect=StorageError("Storage failed")):
            with self.assertRaises(CustomerServiceError) as context:
                self.customer_service.create_customer(
                    "C001", "John Doe", "john@example.com", "123-456-7890"
                )
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_customer_storage_error(self):
        """Test get customer with storage error."""
        with patch.object(self.storage, 'find_customer_by_id', side_effect=StorageError("Storage failed")):
            with self.assertRaises(CustomerServiceError) as context:
                self.customer_service.get_customer("C001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_all_customers_storage_error(self):
        """Test get all customers with storage error."""
        with patch.object(self.storage, 'load_customers', side_effect=StorageError("Storage failed")):
            with self.assertRaises(CustomerServiceError) as context:
                self.customer_service.get_all_customers()
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_update_customer_storage_error(self):
        """Test update customer with storage error."""
        # Create customer first
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )
        
        with patch.object(self.storage, 'save_customer', side_effect=StorageError("Storage failed")):
            with self.assertRaises(CustomerServiceError) as context:
                self.customer_service.update_customer("C001", {"name": "Jane Doe"})
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_delete_customer_storage_error(self):
        """Test delete customer with storage error."""
        with patch.object(self.storage, 'delete_customer', side_effect=StorageError("Storage failed")):
            with self.assertRaises(CustomerServiceError) as context:
                self.customer_service.delete_customer("C001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_display_customer_info_storage_error(self):
        """Test display customer info with storage error."""
        with patch.object(self.storage, 'find_customer_by_id', side_effect=StorageError("Storage failed")):
            with self.assertRaises(CustomerServiceError) as context:
                self.customer_service.display_customer_info("C001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_get_customer_reservations_storage_error(self):
        """Test get customer reservations with storage error."""
        # Create customer first
        self.customer_service.create_customer(
            "C001", "John Doe", "john@example.com", "123-456-7890"
        )
        
        with patch.object(self.storage, 'get_reservations_by_customer', side_effect=StorageError("Storage failed")):
            with self.assertRaises(CustomerServiceError) as context:
                self.customer_service.get_customer_reservations("C001")
            self.assertIn("Storage error: Storage failed", str(context.exception))

    def test_find_customer_by_email_storage_error(self):
        """Test find customer by email with storage error."""
        with patch.object(self.storage, 'load_customers', side_effect=StorageError("Storage failed")):
            with self.assertRaises(CustomerServiceError) as context:
                self.customer_service.find_customer_by_email("test@example.com")
            self.assertIn("Storage error: Storage failed", str(context.exception))


if __name__ == '__main__':
    unittest.main()

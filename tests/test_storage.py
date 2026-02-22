"""
Unit tests for the storage module.
Tests JSONStorage class for persistent data operations.
"""
import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import patch
from src.storage import JSONStorage, StorageError
from src.models import Hotel, Customer, Reservation


class TestJSONStorage(unittest.TestCase):
    """Test cases for the JSONStorage class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = JSONStorage(self.test_dir)

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    # Test directory creation
    def test_data_directory_creation(self):
        """Test that data directory is created."""
        self.assertTrue(os.path.exists(self.test_dir))

    # Hotel storage tests
    def test_save_and_load_hotels_empty(self):
        """Test saving and loading empty hotel list."""
        hotels = []
        self.storage.save_hotels(hotels)
        loaded_hotels = self.storage.load_hotels()
        self.assertEqual(loaded_hotels, [])

    def test_save_and_load_hotels_single(self):
        """Test saving and loading single hotel."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 80)
        self.storage.save_hotels([hotel])

        loaded_hotels = self.storage.load_hotels()
        self.assertEqual(len(loaded_hotels), 1)
        self.assertEqual(loaded_hotels[0].hotel_id, "H001")
        self.assertEqual(loaded_hotels[0].name, "Grand Hotel")

    def test_save_and_load_hotels_multiple(self):
        """Test saving and loading multiple hotels."""
        hotels = [
            Hotel("H001", "Grand Hotel", "NY", 100, 80),
            Hotel("H002", "Beach Resort", "CA", 200, 150)
        ]
        self.storage.save_hotels(hotels)

        loaded_hotels = self.storage.load_hotels()
        self.assertEqual(len(loaded_hotels), 2)
        hotel_ids = [h.hotel_id for h in loaded_hotels]
        self.assertIn("H001", hotel_ids)
        self.assertIn("H002", hotel_ids)

    def test_find_hotel_by_id_exists(self):
        """Test finding hotel by ID when it exists."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 80)
        self.storage.save_hotels([hotel])

        found_hotel = self.storage.find_hotel_by_id("H001")
        self.assertIsNotNone(found_hotel)
        self.assertEqual(found_hotel.hotel_id, "H001")

    def test_find_hotel_by_id_not_exists(self):
        """Test finding hotel by ID when it doesn't exist."""
        found_hotel = self.storage.find_hotel_by_id("H999")
        self.assertIsNone(found_hotel)

    def test_save_hotel_new(self):
        """Test saving a new hotel."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 80)
        self.storage.save_hotel(hotel)

        loaded_hotels = self.storage.load_hotels()
        self.assertEqual(len(loaded_hotels), 1)
        self.assertEqual(loaded_hotels[0].hotel_id, "H001")

    def test_save_hotel_update_existing(self):
        """Test updating an existing hotel."""
        original_hotel = Hotel("H001", "Grand Hotel", "NY", 100, 80)
        self.storage.save_hotel(original_hotel)

        updated_hotel = Hotel("H001", "Updated Hotel", "CA", 150, 120)
        self.storage.save_hotel(updated_hotel)

        loaded_hotels = self.storage.load_hotels()
        self.assertEqual(len(loaded_hotels), 1)
        self.assertEqual(loaded_hotels[0].name, "Updated Hotel")
        self.assertEqual(loaded_hotels[0].location, "CA")

    def test_delete_hotel_exists(self):
        """Test deleting hotel that exists."""
        hotel = Hotel("H001", "Grand Hotel", "NY", 100, 80)
        self.storage.save_hotel(hotel)

        result = self.storage.delete_hotel("H001")
        self.assertTrue(result)

        loaded_hotels = self.storage.load_hotels()
        self.assertEqual(len(loaded_hotels), 0)

    def test_delete_hotel_not_exists(self):
        """Test deleting hotel that doesn't exist."""
        result = self.storage.delete_hotel("H999")
        self.assertFalse(result)

    # Customer storage tests
    def test_save_and_load_customers(self):
        """Test saving and loading customers."""
        customer = Customer("C001", "John Doe", "john@example.com", "123-456-7890")
        self.storage.save_customers([customer])

        loaded_customers = self.storage.load_customers()
        self.assertEqual(len(loaded_customers), 1)
        self.assertEqual(loaded_customers[0].customer_id, "C001")

    def test_find_customer_by_id(self):
        """Test finding customer by ID."""
        customer = Customer("C001", "John Doe", "john@example.com", "123-456-7890")
        self.storage.save_customer(customer)

        found_customer = self.storage.find_customer_by_id("C001")
        self.assertIsNotNone(found_customer)
        self.assertEqual(found_customer.customer_id, "C001")

    def test_delete_customer(self):
        """Test deleting customer."""
        customer = Customer("C001", "John Doe", "john@example.com", "123-456-7890")
        self.storage.save_customer(customer)

        result = self.storage.delete_customer("C001")
        self.assertTrue(result)

        found_customer = self.storage.find_customer_by_id("C001")
        self.assertIsNone(found_customer)

    # Reservation storage tests
    def test_save_and_load_reservations(self):
        """Test saving and loading reservations."""
        reservation = Reservation(
            "R001", "C001", "H001", "2024-12-01", "2024-12-03"
        )
        self.storage.save_reservations([reservation])

        loaded_reservations = self.storage.load_reservations()
        self.assertEqual(len(loaded_reservations), 1)
        self.assertEqual(loaded_reservations[0].reservation_id, "R001")

    def test_find_reservation_by_id(self):
        """Test finding reservation by ID."""
        reservation = Reservation(
            "R001", "C001", "H001", "2024-12-01", "2024-12-03"
        )
        self.storage.save_reservation(reservation)

        found_reservation = self.storage.find_reservation_by_id("R001")
        self.assertIsNotNone(found_reservation)
        self.assertEqual(found_reservation.reservation_id, "R001")

    def test_get_reservations_by_customer(self):
        """Test getting reservations by customer ID."""
        reservations = [
            Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03"),
            Reservation("R002", "C001", "H002", "2024-12-05", "2024-12-07"),
            Reservation("R003", "C002", "H001", "2024-12-10", "2024-12-12")
        ]
        self.storage.save_reservations(reservations)

        customer_reservations = self.storage.get_reservations_by_customer("C001")
        self.assertEqual(len(customer_reservations), 2)

        reservation_ids = [r.reservation_id for r in customer_reservations]
        self.assertIn("R001", reservation_ids)
        self.assertIn("R002", reservation_ids)

    def test_get_reservations_by_hotel(self):
        """Test getting reservations by hotel ID."""
        reservations = [
            Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03"),
            Reservation("R002", "C002", "H001", "2024-12-05", "2024-12-07"),
            Reservation("R003", "C001", "H002", "2024-12-10", "2024-12-12")
        ]
        self.storage.save_reservations(reservations)

        hotel_reservations = self.storage.get_reservations_by_hotel("H001")
        self.assertEqual(len(hotel_reservations), 2)

        reservation_ids = [r.reservation_id for r in hotel_reservations]
        self.assertIn("R001", reservation_ids)
        self.assertIn("R002", reservation_ids)

    # Error handling tests
    def test_load_hotels_nonexistent_file(self):
        """Test loading hotels when file doesn't exist."""
        hotels = self.storage.load_hotels()
        self.assertEqual(hotels, [])

    def test_load_hotels_empty_file(self):
        """Test loading hotels from empty file."""
        # Create empty file
        with open(self.storage.hotels_file, 'w') as f:
            f.write("")

        hotels = self.storage.load_hotels()
        self.assertEqual(hotels, [])

    def test_load_hotels_invalid_json(self):
        """Test loading hotels from file with invalid JSON."""
        # Create file with invalid JSON
        with open(self.storage.hotels_file, 'w') as f:
            f.write("invalid json content")

        with self.assertRaises(StorageError) as context:
            self.storage.load_hotels()
        self.assertIn("Invalid JSON format", str(context.exception))

    def test_load_hotels_invalid_data_format(self):
        """Test loading hotels with invalid data format."""
        # Create file with valid JSON but invalid hotel data
        invalid_data = [{"hotel_id": "H001"}]  # Missing required fields
        with open(self.storage.hotels_file, 'w') as f:
            json.dump(invalid_data, f)

        with self.assertRaises(StorageError) as context:
            self.storage.load_hotels()
        self.assertIn("Invalid hotel data format", str(context.exception))

    def test_load_customers_invalid_json(self):
        """Test loading customers from file with invalid JSON."""
        with open(self.storage.customers_file, 'w') as f:
            f.write("invalid json content")

        with self.assertRaises(StorageError) as context:
            self.storage.load_customers()
        self.assertIn("Invalid JSON format", str(context.exception))

    def test_load_reservations_invalid_json(self):
        """Test loading reservations from file with invalid JSON."""
        with open(self.storage.reservations_file, 'w') as f:
            f.write("invalid json content")

        with self.assertRaises(StorageError) as context:
            self.storage.load_reservations()
        self.assertIn("Invalid JSON format", str(context.exception))

    def test_write_to_readonly_directory(self):
        """Test writing to read-only directory raises StorageError."""
        if os.name != 'nt':  # Skip on Windows
            readonly_dir = tempfile.mkdtemp()
            try:
                os.chmod(readonly_dir, 0o444)  # Read-only
                readonly_storage = JSONStorage(readonly_dir)

                hotel = Hotel("H001", "Grand Hotel", "NY", 100, 80)
                with self.assertRaises(StorageError) as context:
                    readonly_storage.save_hotel(hotel)
                self.assertIn("Error writing to file", str(context.exception))
            finally:
                os.chmod(readonly_dir, 0o755)  # Restore permissions
                shutil.rmtree(readonly_dir)

    def test_concurrent_file_operations(self):
        """Test that multiple operations work correctly."""
        # Save hotels
        hotels = [Hotel("H001", "Hotel1", "NY", 100, 80)]
        self.storage.save_hotels(hotels)

        # Save customers
        customers = [Customer("C001", "John", "john@test.com", "123")]
        self.storage.save_customers(customers)

        # Save reservations
        reservations = [Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03")]
        self.storage.save_reservations(reservations)

        # Verify all data is saved correctly
        self.assertEqual(len(self.storage.load_hotels()), 1)
        self.assertEqual(len(self.storage.load_customers()), 1)
        self.assertEqual(len(self.storage.load_reservations()), 1)

    def test_json_file_encoding(self):
        """Test that JSON files handle Unicode characters correctly."""
        hotel = Hotel("H001", "Hôtel Français", "Montréal", 100, 80)
        customer = Customer("C001", "José García", "jose@example.com", "123")

        self.storage.save_hotel(hotel)
        self.storage.save_customer(customer)

        loaded_hotel = self.storage.find_hotel_by_id("H001")
        loaded_customer = self.storage.find_customer_by_id("C001")

        self.assertEqual(loaded_hotel.name, "Hôtel Français")
        self.assertEqual(loaded_hotel.location, "Montréal")
        self.assertEqual(loaded_customer.name, "José García")

    def test_create_data_directory(self):
        """Test creating data directory when it doesn't exist."""
        # Create storage with non-existent directory
        new_storage = JSONStorage("test_new_data")
        
        # This should create the directory
        hotel = Hotel("H001", "Test Hotel", "Test Location", 100, 80)
        new_storage.save_hotel(hotel)
        
        # Verify directory was created and file was saved
        self.assertTrue(os.path.exists("test_new_data"))
        self.assertTrue(os.path.exists("test_new_data/hotels.json"))
        
        # Clean up
        import shutil
        shutil.rmtree("test_new_data")

    def test_read_json_file_empty(self):
        """Test reading empty JSON file."""
        # Create empty file
        empty_file = os.path.join(self.test_dir, "empty.json")
        with open(empty_file, 'w') as f:
            pass  # Create empty file
        
        # Test reading empty file
        result = self.storage._read_json_file(empty_file)
        self.assertEqual(result, [])

    def test_read_json_file_invalid_json(self):
        """Test reading file with invalid JSON."""
        # Create file with invalid JSON
        invalid_file = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        # Test reading invalid JSON file
        with self.assertRaises(StorageError):
            self.storage._read_json_file(invalid_file)

    def test_create_directory_success(self):
        """Test creating directory successfully."""
        # Create storage instance with a new directory path
        new_dir = os.path.join(self.test_dir, "new_subdir")
        storage = JSONStorage(new_dir)
        
        # Save a hotel which should trigger directory creation
        hotel = Hotel("H001", "Test Hotel", "Test Location", 100, 80)
        storage.save_hotel(hotel)
        
        # Verify directory was created
        self.assertTrue(os.path.exists(new_dir))
        
    def test_json_file_operations_edge_cases(self):
        """Test edge cases in JSON file operations."""
        # Test with empty data list
        empty_data = []
        file_path = os.path.join(self.test_dir, "empty_data.json")
        
        # Write empty data
        self.storage._write_json_file(file_path, empty_data)
        
        # Read it back
        result = self.storage._read_json_file(file_path)
        self.assertEqual(result, [])

    def test_read_json_file_not_found_after_creation(self):
        """Test reading file that doesn't exist but directory exists."""
        # Create a file path that doesn't exist but in existing directory
        non_existent_file = os.path.join(self.test_dir, "non_existent.json")
        
        # Test reading non-existent file (should return empty list)
        result = self.storage._read_json_file(non_existent_file)
        self.assertEqual(result, [])

    def test_load_customers_invalid_data_format(self):
        """Test loading customers with invalid data format."""
        # Create file with customer data missing required fields
        invalid_data = [{"customer_id": "C001"}]  # Missing required fields
        customers_file = os.path.join(self.test_dir, "customers.json")
        
        with open(customers_file, 'w') as f:
            json.dump(invalid_data, f)
        
        with self.assertRaises(StorageError) as context:
            self.storage.load_customers()
        self.assertIn("Invalid customer data format", str(context.exception))

    def test_load_hotels_invalid_data_format(self):
        """Test loading hotels with invalid data format."""
        # Create file with hotel data missing required fields
        invalid_data = [{"hotel_id": "H001"}]  # Missing required fields
        hotels_file = os.path.join(self.test_dir, "hotels.json")
        
        with open(hotels_file, 'w') as f:
            json.dump(invalid_data, f)
        
        with self.assertRaises(StorageError) as context:
            self.storage.load_hotels()
        self.assertIn("Invalid hotel data format", str(context.exception))

    def test_load_reservations_invalid_data_format(self):
        """Test loading reservations with invalid data format."""
        # Create file with reservation data missing required fields
        invalid_data = [{"reservation_id": "R001"}]  # Missing required fields
        reservations_file = os.path.join(self.test_dir, "reservations.json")
        
        with open(reservations_file, 'w') as f:
            json.dump(invalid_data, f)
        
        with self.assertRaises(StorageError) as context:
            self.storage.load_reservations()
        self.assertIn("Invalid reservation data format", str(context.exception))

    def test_read_json_file_io_error(self):
        """Test reading JSON file with IO error."""
        # Create a file and then make it inaccessible
        test_file = os.path.join(self.test_dir, "test_io.json")
        with open(test_file, 'w') as f:
            json.dump([], f)
        
        # Make file unreadable
        os.chmod(test_file, 0o000)
        
        try:
            with self.assertRaises(StorageError) as context:
                self.storage._read_json_file(test_file)
            self.assertIn("Error reading file", str(context.exception))
        finally:
            # Restore permissions for cleanup
            os.chmod(test_file, 0o644)

    def test_delete_reservation_exists(self):
        """Test deleting existing reservation."""
        # Create and save a reservation first
        reservation = Reservation("R001", "C001", "H001", "2024-12-01", "2024-12-03")
        self.storage.save_reservation(reservation)
        
        # Verify it exists
        found = self.storage.find_reservation_by_id("R001")
        self.assertIsNotNone(found)
        
        # Delete it
        result = self.storage.delete_reservation("R001")
        self.assertTrue(result)
        
        # Verify it's gone
        found = self.storage.find_reservation_by_id("R001")
        self.assertIsNone(found)

    def test_delete_reservation_not_exists(self):
        """Test deleting non-existent reservation."""
        result = self.storage.delete_reservation("R999")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

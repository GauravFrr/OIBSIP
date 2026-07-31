import unittest
import os
import sqlite3
from bmi_calculator import calc_bmi, get_category, init_db, save_record, get_user_history, get_unique_users

class TestBMICalculator(unittest.TestCase):
    
    def setUp(self):
        # We will use a separate test db for clean testing
        # Patch the database name dynamically in sqlite3 if possible, 
        # or just make sure we back up/restore or cleanup.
        # To keep it simple, we will clean up bmi_records.db after tests.
        if os.path.exists("bmi_records.db"):
            os.remove("bmi_records.db")
        init_db()

    def tearDown(self):
        # Clean up database file after test run
        if os.path.exists("bmi_records.db"):
            os.remove("bmi_records.db")

    def test_calc_bmi(self):
        # Test standard calculations
        self.assertEqual(calc_bmi(70, 1.75), 22.86)
        self.assertEqual(calc_bmi(50, 1.60), 19.53)
        self.assertEqual(calc_bmi(90, 1.80), 27.78)

    def test_get_category(self):
        # Underweight (< 18.5)
        cat, color = get_category(18.4)
        self.assertEqual(cat, "Underweight")
        
        # Normal (18.5 - 24.99)
        cat, color = get_category(18.5)
        self.assertEqual(cat, "Normal")
        cat, color = get_category(24.9)
        self.assertEqual(cat, "Normal")
        
        # Overweight (25 - 29.99)
        cat, color = get_category(25.0)
        self.assertEqual(cat, "Overweight")
        cat, color = get_category(29.9)
        self.assertEqual(cat, "Overweight")
        
        # Obese (>= 30)
        cat, color = get_category(30.0)
        self.assertEqual(cat, "Obese")
        cat, color = get_category(35.5)
        self.assertEqual(cat, "Obese")

    def test_database_flow(self):
        # Save records and test querying
        save_record("TestUser", 70.0, 1.75, 22.86, "Normal")
        save_record("TestUser", 75.0, 1.75, 24.49, "Normal")
        save_record("OtherUser", 90.0, 1.80, 27.78, "Overweight")

        # Test listing unique users
        users = get_unique_users()
        self.assertIn("TestUser", users)
        self.assertIn("OtherUser", users)
        self.assertEqual(len(users), 2)

        # Test fetching user history
        history = get_user_history("TestUser")
        self.assertEqual(len(history), 2)
        # First entry check: bmi, weight, height
        self.assertEqual(history[0][0], 22.86)
        self.assertEqual(history[0][2], 70.0)
        self.assertEqual(history[0][3], 1.75)
        
        # Second entry check
        self.assertEqual(history[1][0], 24.49)
        
        # Other user check
        other_history = get_user_history("OtherUser")
        self.assertEqual(len(other_history), 1)
        self.assertEqual(other_history[0][0], 27.78)

if __name__ == "__main__":
    unittest.main()


import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Adjust path to import core
sys.path.append(os.getcwd())

from core.auth import AuthManager
import config

class TestPermissions(unittest.TestCase):
    
    def setUp(self):
        # Mock DB
        self.mock_db_patcher = patch('core.auth.db')
        self.mock_db = self.mock_db_patcher.start()
        
        self.auth = AuthManager()
        
    def tearDown(self):
        self.mock_db_patcher.stop()
        
    def test_default_permissions(self):
        """Test fallback to default role permissions"""
        from datetime import datetime
        self.auth.current_user = {'id': 1, 'role': 'admin'}
        self.auth.session_start = datetime.now() # Fake authorized
        self.mock_db.fetch_one.return_value = None # No overrides
        
        # Admin should have manage_products
        self.assertTrue(self.auth.has_permission('manage_products'))
        
        # Cashier user
        self.auth.current_user = {'id': 2, 'role': 'cashier'}
        self.mock_db.fetch_one.return_value = None
        
        # Cashier should NOT have manage_users
        self.assertFalse(self.auth.has_permission('manage_users'))
        # But should have make_sales
        self.assertTrue(self.auth.has_permission('make_sales'))
        
    def test_permission_override_grant(self):
        """Test granting a permission usually denied"""
        from datetime import datetime
        self.auth.current_user = {'id': 2, 'role': 'cashier'}
        self.auth.session_start = datetime.now()
        
        # Simulate DB returning is_granted=1 for manage_products
        self.mock_db.fetch_one.return_value = {'is_granted': 1}
        
        self.assertTrue(self.auth.has_permission('manage_products'))
        
        # Check that DB was called correctly
        # call_args returns (args, kwargs)
        args, _ = self.mock_db.fetch_one.call_args
        self.assertIn("SELECT is_granted FROM user_permissions", args[0])
        self.assertEqual(args[1], (2, 'manage_products'))
        
    def test_permission_override_deny(self):
        """Test denying a permission usually granted"""
        from datetime import datetime
        self.auth.current_user = {'id': 2, 'role': 'cashier'}
        self.auth.session_start = datetime.now()
        
        # Simulate DB returning is_granted=0 for make_sales
        self.mock_db.fetch_one.return_value = {'is_granted': 0}
        
        self.assertFalse(self.auth.has_permission('make_sales'))

if __name__ == '__main__':
    unittest.main()

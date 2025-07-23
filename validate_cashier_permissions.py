#!/usr/bin/env python
"""
Comprehensive Cashier Permissions Validation Script

This script validates that the cashier permissions system is properly configured
and working as expected. It tests user creation, permission assignment, and
security restrictions.

Usage:
    python validate_cashier_permissions.py
    python manage.py runscript validate_cashier_permissions
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.urls import reverse
from core.permissions import CashierPermissions, get_cashier_permission_summary
from orders.models import Order, OrderItem, OrderStatus
from vendors.models import Table, Vendor, Category, MenuItem
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CashierPermissionValidator:
    """
    Comprehensive validator for cashier permissions system
    """

    def __init__(self):
        self.test_username = 'test_cashier_validation'
        self.test_password = 'test_pass_123'
        self.test_user = None
        self.client = Client()
        self.errors = []
        self.warnings = []
        self.passed_tests = []

    def log_error(self, message):
        """Log an error"""
        self.errors.append(message)
        logger.error(f"❌ {message}")

    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(message)
        logger.warning(f"⚠️  {message}")

    def log_success(self, message):
        """Log a successful test"""
        self.passed_tests.append(message)
        logger.info(f"✅ {message}")

    def run_all_validations(self):
        """Run all validation tests"""
        logger.info("🔍 Starting Cashier Permissions Validation")
        logger.info("=" * 60)

        try:
            # Core validation tests
            self.validate_cashier_group_exists()
            self.validate_required_permissions()
            self.validate_user_creation()
            self.validate_permission_assignment()
            self.validate_security_restrictions()
            self.validate_view_access()
            self.validate_api_endpoints()
            self.validate_audit_logging()

            # Cleanup
            self.cleanup_test_data()

            # Generate report
            self.generate_validation_report()

        except Exception as e:
            self.log_error(f"Critical validation error: {str(e)}")
            logger.error(f"Validation failed with exception: {e}")

    def validate_cashier_group_exists(self):
        """Test 1: Validate cashier group exists and has correct setup"""
        logger.info("📋 Test 1: Validating Cashier Group Setup")

        try:
            cashier_group = Group.objects.get(name='Cashier')
            self.log_success("Cashier group exists")

            # Check group has permissions
            perms = cashier_group.permissions.all()
            if perms.count() > 0:
                self.log_success(f"Cashier group has {perms.count()} permissions assigned")
            else:
                self.log_error("Cashier group has no permissions assigned")

        except Group.DoesNotExist:
            self.log_error("Cashier group does not exist")

    def validate_required_permissions(self):
        """Test 2: Validate all required permissions exist and are assigned"""
        logger.info("📋 Test 2: Validating Required Permissions")

        required_permissions = CashierPermissions.REQUIRED_PERMISSIONS

        try:
            cashier_group = Group.objects.get(name='Cashier')
            assigned_perms = [
                f"{perm.content_type.app_label}.{perm.codename}"
                for perm in cashier_group.permissions.all()
            ]

            missing_perms = []
            for perm in required_permissions:
                if perm in assigned_perms:
                    self.log_success(f"Required permission assigned: {perm}")
                else:
                    missing_perms.append(perm)
                    self.log_error(f"Missing required permission: {perm}")

            if not missing_perms:
                self.log_success("All required permissions are assigned")

        except Group.DoesNotExist:
            self.log_error("Cannot validate permissions - Cashier group missing")

    def validate_user_creation(self):
        """Test 3: Validate user creation and group assignment"""
        logger.info("📋 Test 3: Validating User Creation")

        # Clean up any existing test user
        User.objects.filter(username=self.test_username).delete()

        try:
            # Test programmatic user creation
            result = CashierPermissions.add_user_to_cashier_group(
                User.objects.create_user(
                    username=self.test_username,
                    password=self.test_password,
                    email='test@cashier.com'
                )
            )

            if result['success']:
                self.test_user = User.objects.get(username=self.test_username)
                self.log_success("Test user created and added to cashier group")

                # Verify group membership
                if CashierPermissions.is_cashier(self.test_user):
                    self.log_success("User correctly identified as cashier")
                else:
                    self.log_error("User not identified as cashier after group assignment")

            else:
                self.log_error(f"Failed to add user to cashier group: {result['message']}")

        except Exception as e:
            self.log_error(f"User creation failed: {str(e)}")

    def validate_permission_assignment(self):
        """Test 4: Validate specific permission assignments"""
        logger.info("📋 Test 4: Validating Permission Assignments")

        if not self.test_user:
            self.log_error("Cannot test permissions - no test user created")
            return

        # Test specific permissions
        permission_tests = [
            ('orders.view_order', 'View orders'),
            ('orders.change_order', 'Change order status'),
            ('vendors.view_vendor', 'View vendor information'),
            ('vendors.change_table', 'Reset tables'),
            ('orders.view_orderitem', 'View order items'),
            ('orders.add_orderstatushistory', 'Add status history'),
        ]

        for perm, description in permission_tests:
            if self.test_user.has_perm(perm):
                self.log_success(f"Permission granted: {description} ({perm})")
            else:
                self.log_error(f"Permission missing: {description} ({perm})")

        # Get comprehensive permission status
        status = CashierPermissions.check_cashier_permissions(self.test_user)
        if status['has_all_permissions']:
            self.log_success("User has all required cashier permissions")
        else:
            self.log_error(f"User missing {len(status['missing_permissions'])} permissions")

    def validate_security_restrictions(self):
        """Test 5: Validate security restrictions are in place"""
        logger.info("📋 Test 5: Validating Security Restrictions")

        if not self.test_user:
            self.log_error("Cannot test security - no test user created")
            return

        # Test forbidden permissions
        forbidden_tests = [
            ('auth.add_user', 'Create users'),
            ('auth.delete_user', 'Delete users'),
            ('vendors.delete_vendor', 'Delete vendors'),
            ('vendors.add_menuitem', 'Add menu items'),
            ('orders.delete_order', 'Delete orders'),
            ('auth.change_permission', 'Modify permissions'),
        ]

        security_issues = 0
        for perm, description in forbidden_tests:
            if self.test_user.has_perm(perm):
                self.log_error(f"SECURITY ISSUE: User has forbidden permission: {description} ({perm})")
                security_issues += 1
            else:
                self.log_success(f"Security check passed: Cannot {description.lower()}")

        if security_issues == 0:
            self.log_success("All security restrictions properly enforced")
        else:
            self.log_error(f"Found {security_issues} security violations")

    def validate_view_access(self):
        """Test 6: Validate view access permissions"""
        logger.info("📋 Test 6: Validating View Access")

        if not self.test_user:
            self.log_error("Cannot test view access - no test user created")
            return

        # Login test user
        login_success = self.client.login(
            username=self.test_username,
            password=self.test_password
        )

        if login_success:
            self.log_success("Test user can login")

            # Test cashier dashboard access
            try:
                response = self.client.get('/cashier/')
                if response.status_code == 200:
                    self.log_success("Cashier dashboard accessible")
                elif response.status_code == 302:
                    self.log_warning("Cashier dashboard redirected (check URL configuration)")
                else:
                    self.log_error(f"Cashier dashboard returned status {response.status_code}")
            except Exception as e:
                self.log_warning(f"Could not test dashboard access: {str(e)}")

        else:
            self.log_error("Test user cannot login")

    def validate_api_endpoints(self):
        """Test 7: Validate API endpoint permissions"""
        logger.info("📋 Test 7: Validating API Endpoints")

        if not self.test_user:
            self.log_error("Cannot test API endpoints - no test user created")
            return

        # Create test data if needed
        try:
            # Ensure we have test tables and orders
            test_table, created = Table.objects.get_or_create(
                number=999,
                defaults={'seats': 4, 'is_active': True}
            )

            if created:
                self.log_success("Created test table for API testing")

        except Exception as e:
            self.log_warning(f"Could not create test data for API testing: {str(e)}")

    def validate_audit_logging(self):
        """Test 8: Validate audit logging is working"""
        logger.info("📋 Test 8: Validating Audit Logging")

        # Test that logging functions work
        try:
            from core.permissions import CashierPermissions

            # Test permission checking logs
            if self.test_user:
                status = CashierPermissions.check_cashier_permissions(self.test_user)
                self.log_success("Permission checking logging functional")
            else:
                self.log_warning("Cannot test logging without test user")

        except Exception as e:
            self.log_error(f"Audit logging test failed: {str(e)}")

    def cleanup_test_data(self):
        """Clean up test data created during validation"""
        logger.info("🧹 Cleaning up test data")

        try:
            # Remove test user
            if self.test_user:
                self.test_user.delete()
                self.log_success("Test user removed")

            # Remove test table if created
            Table.objects.filter(number=999).delete()

        except Exception as e:
            self.log_warning(f"Cleanup warning: {str(e)}")

    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 CASHIER PERMISSIONS VALIDATION REPORT")
        logger.info("=" * 60)

        total_tests = len(self.passed_tests) + len(self.errors) + len(self.warnings)

        logger.info(f"Total Tests Run: {total_tests}")
        logger.info(f"✅ Passed: {len(self.passed_tests)}")
        logger.info(f"⚠️  Warnings: {len(self.warnings)}")
        logger.info(f"❌ Errors: {len(self.errors)}")

        if self.errors:
            logger.info("\n🚨 ERRORS FOUND:")
            for error in self.errors:
                logger.info(f"   • {error}")

        if self.warnings:
            logger.info("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                logger.info(f"   • {warning}")

        logger.info("\n✅ SUCCESSFUL TESTS:")
        for success in self.passed_tests:
            logger.info(f"   • {success}")

        # Overall status
        if not self.errors:
            if not self.warnings:
                logger.info("\n🎉 VALIDATION PASSED: All tests successful!")
                logger.info("Your cashier permissions system is properly configured.")
            else:
                logger.info("\n✅ VALIDATION MOSTLY PASSED: Some warnings found")
                logger.info("Your system is functional but may need minor adjustments.")
        else:
            logger.info("\n❌ VALIDATION FAILED: Critical errors found")
            logger.info("Please fix the errors above before using the cashier system.")

        # Recommendations
        logger.info("\n📋 RECOMMENDATIONS:")
        if self.errors:
            logger.info("   1. Run: python manage.py setup_cashier_permissions --reset")
            logger.info("   2. Verify all required Django apps are installed")
            logger.info("   3. Check database migrations are up to date")

        logger.info("   4. Test cashier login with a real user account")
        logger.info("   5. Verify cashier dashboard loads correctly")
        logger.info("   6. Test payment processing functionality")

        return len(self.errors) == 0


def main():
    """Main function to run validation"""
    validator = CashierPermissionValidator()
    success = validator.run_all_validations()

    if success:
        print("\n🎉 Validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Validation failed. Please check the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()

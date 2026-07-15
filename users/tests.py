# users/tests.py
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers

from .serializers import AdminUserSerializer


class AdminUserSerializerBirthDateTests(TestCase):
    """
    Tests for the now-active `validate_birth_date` rule in AdminUserSerializer.

    Previously `birth_date` was neither a model field nor in the serializer
    `fields`, so DRF never called the validator. After adding the `birth_date`
    column to the User model and to the serializer fields, the 19+ age rule and
    future-date rule are enforced.
    """

    @staticmethod
    def _payload(**overrides):
        payload = {
            "username": "test_admin",
            "first_name": "Test",
            "last_name": "Admin",
        }
        payload.update(overrides)
        return payload

    def test_adult_birth_date_passes(self):
        """A birth_date corresponding to 19+ years must pass validation."""
        birth_date = (timezone.now().date() - timedelta(days=365 * 25)).isoformat()
        serializer = AdminUserSerializer(data=self._payload(birth_date=birth_date))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_underage_birth_date_fails(self):
        """A birth_date corresponding to under 19 years must fail validation."""
        birth_date = (timezone.now().date() - timedelta(days=365 * 10)).isoformat()
        serializer = AdminUserSerializer(data=self._payload(birth_date=birth_date))
        self.assertFalse(serializer.is_valid())
        self.assertIn("birth_date", serializer.errors)

    def test_future_birth_date_fails(self):
        """A birth_date in the future must fail validation."""
        birth_date = (timezone.now().date() + timedelta(days=365)).isoformat()
        serializer = AdminUserSerializer(data=self._payload(birth_date=birth_date))
        self.assertFalse(serializer.is_valid())
        self.assertIn("birth_date", serializer.errors)

    def test_missing_birth_date_is_allowed(self):
        """birth_date is optional, so omitting it must not fail validation."""
        serializer = AdminUserSerializer(data=self._payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_validate_birth_date_raises_on_underage(self):
        """The field validator itself must raise a DRF ValidationError for minors."""
        serializer = AdminUserSerializer()
        underage = timezone.now().date() - timedelta(days=365 * 10)
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_birth_date(underage)

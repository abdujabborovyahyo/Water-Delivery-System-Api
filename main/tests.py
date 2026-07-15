# main/tests.py
from decimal import Decimal

from django.test import TestCase
from rest_framework import serializers

from .serializers import WaterSerializer


class WaterSerializerValidateLitersTests(TestCase):
    """
    Tests for the `validate_liters` fix in WaterSerializer.

    Previously the validator did `value.liters > 19`, but `value` is the
    `liters` field value (a Decimal) itself, which raised an AttributeError
    (500 error) on every create/update. The fix compares `value > 19`.
    """

    @staticmethod
    def _base_payload(**overrides):
        payload = {
            "brand_name": "Test Suv",
            "price": "5000.00",
            "liters": "19.00",
            "description": "Test brendi",
            "is_available": True,
        }
        payload.update(overrides)
        return payload

    def test_valid_liters_passes_validation(self):
        """A value of 19 or less must pass validation without errors."""
        serializer = WaterSerializer(data=self._base_payload(liters="19.00"))
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["liters"], Decimal("19.00"))

    def test_liters_above_limit_fails_validation(self):
        """A value greater than 19 must fail validation with an error on `liters`."""
        serializer = WaterSerializer(data=self._base_payload(liters="20.00"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("liters", serializer.errors)

    def test_validate_liters_does_not_crash_on_decimal(self):
        """
        Regression test: the field-level validator must accept a Decimal
        directly and not attempt to access a non-existent `.liters` attribute.
        """
        serializer = WaterSerializer()
        # Valid value is returned unchanged.
        self.assertEqual(serializer.validate_liters(Decimal("10.00")), Decimal("10.00"))
        # Invalid value raises a DRF ValidationError (not AttributeError).
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_liters(Decimal("25.00"))

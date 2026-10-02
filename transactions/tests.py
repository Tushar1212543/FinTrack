from django.test import TestCase

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework.test import APIClient

from .models import Category, Investment, Transaction


class FinTrackAPITests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            password="TestPass123!"
        )

        self.user2 = User.objects.create_user(
            username="user2",
            password="TestPass456!"
        )

        self.client = APIClient()

    def test_unauthenticated_transaction_list_is_rejected(self):
        response = self.client.get(
            "/transactions/",
            response = self.client.get(
    "/transactions/"
)
        )

        self.assertEqual(response.status_code, 401)

    def test_user_cannot_access_another_users_transaction(self):
        transaction = Transaction.objects.create(
            user=self.user1,
            amount=Decimal("500.00"),
            transaction_type="EXPENSE",
            description="Private Transaction"
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.get(
            f"/transactions/{transaction.id}/",
            response = self.client.get(
    "/transactions/"
)
        )

        self.assertEqual(response.status_code, 404)

    def test_negative_transaction_amount_is_rejected(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.post(
            "/transactions/create/",
            {
                "amount": "-500.00",
                "transaction_type": "EXPENSE",
                "description": "Invalid Amount"
            },
            format="json",
            response = self.client.get(
    "/transactions/"
)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            Transaction.objects.filter(
                user=self.user1
            ).count(),
            0
        )

    def test_user_cannot_use_another_users_category(self):
        category = Category.objects.create(
            user=self.user1,
            name="Private Category"
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.post(
            "/transactions/create/",
            {
                "amount": "100.00",
                "transaction_type": "EXPENSE",
                "description": "Category Security Test",
                "category": category.id
            },
            format="json",
            response = self.client.get(
    "/transactions/"
)
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(
            Transaction.objects.filter(
                user=self.user2,
                description="Category Security Test"
            ).exists()
        )

    def test_user_cannot_access_another_users_investment(self):
        investment = Investment.objects.create(
            user=self.user1,
            symbol="RELIANCE",
            quantity=Decimal("1.0000"),
            buy_price=Decimal("2500.00")
        )

        self.client.force_authenticate(user=self.user2)

        response = self.client.get(
            f"/investments/{investment.id}/",
            response = self.client.get(
    "/transactions/"
)
        )

        self.assertEqual(response.status_code, 404)

    def test_invalid_investment_values_are_rejected(self):
        self.client.force_authenticate(user=self.user1)

        response1 = self.client.post(
            "/investments/create/",
            {
                "symbol": "AAPL",
                "quantity": "0",
                "buy_price": "100"
            },
            format="json",
            response = self.client.get(
    "/transactions/"
)
        )

        response2 = self.client.post(
            "/investments/create/",
            {
                "symbol": "AAPL",
                "quantity": "1",
                "buy_price": "-100"
            },
            format="json",
            response = self.client.get(
    "/transactions/"
)
        )

        self.assertEqual(response1.status_code, 400)
        self.assertEqual(response2.status_code, 400)

        self.assertEqual(
            Investment.objects.filter(
                user=self.user1
            ).count(),
            0
        )
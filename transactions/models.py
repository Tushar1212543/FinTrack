from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_category_per_user"
            )
        ]

    def __str__(self):
        return self.name

class Transaction(models.Model):

    TRANSACTION_TYPES = [
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    transaction_type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPES
    )

    description = models.CharField(
        max_length=255,
        blank=True
    )

    date = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.amount} | {self.transaction_type} | {self.category} | {self.date}"


class Investment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="investments"
    )

    symbol = models.CharField(
        max_length=20
    )

    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4
    )

    buy_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    purchase_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.symbol} | {self.quantity} @ {self.buy_price}"
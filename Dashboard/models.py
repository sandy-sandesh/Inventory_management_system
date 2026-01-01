from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sn = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def SN(self):
        return self.sn

    def __str__(self):
        return f"{self.name} ({self.SN})"


class Transaction(models.Model):
    """Simple transaction model to record sales amounts for aggregation.

    - item: optional ForeignKey to Item
    - amount: Decimal total for the transaction
    - created_at: timestamp
    """
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        item_label = self.item.name if self.item else 'Unknown'
        return f"{item_label} - ${self.amount:.2f} on {self.created_at.date()}"
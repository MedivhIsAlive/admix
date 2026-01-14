import uuid

from django.db import models
from django.conf import settings


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]


class OrderItem1(models.Model):
    order = models.ForeignKey(Order, related_name="item1", on_delete=models.CASCADE, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["order", "created_at"]),
        ]


class OrderItem2(models.Model):
    order = models.ForeignKey(Order, related_name="item2", on_delete=models.CASCADE, db_index=True)
    placement_price = models.DecimalField(max_digits=10, decimal_places=2)
    article_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["order", "created_at"]),
        ]

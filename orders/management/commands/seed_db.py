import random
import uuid
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from orders.models import Order, OrderItem1, OrderItem2


User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with a large amount of random data (pressure testing)"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=1000)
        parser.add_argument("--orders-per-user", type=int, default=50)
        parser.add_argument("--items-per-order", type=int, default=10)
        parser.add_argument("--batch-size", type=int, default=5000)

    @transaction.atomic
    def handle(self, *args, **opts):
        self.stdout.write(f"{opts}")
        users_n = opts["users"]
        orders_n = opts["orders_per_user"]
        items_n = opts["items_per_order"]
        batch = opts["batch_size"]

        now = timezone.now()

        self.stdout.write(self.style.WARNING("Seeding users..."))

        users = [
            User(
                id=uuid.uuid4(),
                username=f"user_{i}",
                email=f"user_{i}@example.com",
                is_active=True,
                date_joined=now - timedelta(days=random.randint(0, 365)),
            )
            for i in range(users_n)
        ]

        User.objects.bulk_create(users, batch_size=batch)
        self.stdout.write(self.style.SUCCESS(f"Users: {len(users)}"))

        self.stdout.write(self.style.WARNING("Seeding orders..."))

        orders = []
        for user in users:
            for _ in range(orders_n):
                orders.append(
                    Order(
                        id=uuid.uuid4(),
                        user=user,
                        created_at=now - timedelta(days=random.randint(0, 365)),
                    )
                )

        Order.objects.bulk_create(orders, batch_size=batch)
        self.stdout.write(self.style.SUCCESS(f"Orders: {len(orders)}"))

        self.stdout.write(self.style.WARNING("Seeding order items (chunked)..."))

        item1_buf = []
        item2_buf = []

        for idx, order in enumerate(orders, start=1):
            for _ in range(items_n):
                ts = now - timedelta(days=random.randint(0, 365))

                item1_buf.append(
                    OrderItem1(
                        order=order,
                        price=Decimal(str(random.uniform(1, 500))).quantize(Decimal("0.01")),
                        created_at=ts,
                    )
                )

                item2_buf.append(
                    OrderItem2(
                        order=order,
                        placement_price=Decimal(str(random.uniform(10, 300))).quantize(Decimal("0.01")),
                        article_price=Decimal(str(random.uniform(5, 200))).quantize(Decimal("0.01")),
                        created_at=ts,
                    )
                )

            if idx % 1000 == 0:
                OrderItem1.objects.bulk_create(item1_buf, batch_size=batch)
                OrderItem2.objects.bulk_create(item2_buf, batch_size=batch)
                item1_buf.clear()
                item2_buf.clear()

        if item1_buf:
            OrderItem1.objects.bulk_create(item1_buf, batch_size=batch)
            OrderItem2.objects.bulk_create(item2_buf, batch_size=batch)

        self.stdout.write(self.style.SUCCESS("Database fully seeded 🚀"))


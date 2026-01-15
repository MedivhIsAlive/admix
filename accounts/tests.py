import random
import uuid
from datetime import timedelta
from decimal import Decimal

from django.db.models import Case, When, Value, DateTimeField, Count, Sum, F
from django.db.models.functions import Coalesce
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model


from orders.models import Order, OrderItem1, OrderItem2
from report import generate_user_orders_report, print_report_by_rows
from report.chrono import as_aware_datetime
from report.period import Period

User = get_user_model()


def get_start_end_datetime():
    return (
        as_aware_datetime(timezone.now() - timedelta(days=60)),
        as_aware_datetime(timezone.now(), end_of_day=True),
    )


class TestReport(TestCase):
    USERS = 50
    ORDERS_PER_USER = 50
    ITEMS_PER_ORDER = 10
    BATCH = 500
    FLUSH_EVERY_ORDERS = 250

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()

        def rand_dt(days_back: int = 120):
            return now - timedelta(days=random.randint(0, days_back))

        def rand_money(a: int, b: int) -> Decimal:
            return Decimal(str(random.uniform(a, b))).quantize(Decimal("0.01"))

        users = [
            User(
                id=uuid.uuid4(),
                username=f"user_{i}",
                email=f"user_{i}@example.com",
                is_active=True,
                date_joined=rand_dt(),
            )
            for i in range(cls.USERS)
        ]
        join_map = {u.id: u.date_joined for u in users}
        User.objects.bulk_create(users, batch_size=cls.BATCH)
        whens = [When(id=user_id, then=Value(dt)) for user_id, dt in join_map.items()]
        User.objects.filter(id__in=join_map.keys()).update(
            date_joined=Case(*whens, output_field=DateTimeField())
        )
        users = list(User.objects.only("id"))

        orders = []
        for u in users:
            for _ in range(cls.ORDERS_PER_USER):
                orders.append(
                    Order(
                        id=uuid.uuid4(),
                        user=u,
                        created_at=rand_dt(),
                    )
                )
        Order.objects.bulk_create(orders, batch_size=cls.BATCH)

        orders = list(Order.objects.only("id"))

        item1_buf: list[OrderItem1] = []
        item2_buf: list[OrderItem2] = []

        for idx, order in enumerate(orders, start=1):
            for _ in range(cls.ITEMS_PER_ORDER):
                item1_buf.append(
                    OrderItem1(
                        order=order,
                        price=rand_money(1, 500),
                        created_at=rand_dt(),
                    )
                )
                item2_buf.append(
                    OrderItem2(
                        order=order,
                        placement_price=rand_money(10, 300),
                        article_price=rand_money(5, 200),
                        created_at=rand_dt(),
                    )
                )

            if idx % cls.FLUSH_EVERY_ORDERS == 0:
                OrderItem1.objects.bulk_create(item1_buf, batch_size=cls.BATCH)
                OrderItem2.objects.bulk_create(item2_buf, batch_size=cls.BATCH)
                item1_buf.clear()
                item2_buf.clear()

        if item1_buf:
            OrderItem1.objects.bulk_create(item1_buf, batch_size=cls.BATCH)
            OrderItem2.objects.bulk_create(item2_buf, batch_size=cls.BATCH)

    def setUp(self):
        self.url = reverse('user-orders-report')
        self.maxDiff = None
        self.user = User.objects.create(username="testuser", email="test@example.com")

    def test_report_under_pressure(self):
        start_date, end_date = get_start_end_datetime()

        users_filtered = User.objects.filter(date_joined__gte=start_date, date_joined__lt=end_date).order_by("date_joined")
        report_rows = list(generate_user_orders_report(start=start_date, end=end_date, period=Period.DAILY))

        response = self.client.get(
            self.url,
            {
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat(),
                "period": Period.DAILY,
            }
        )
        response_rows = response.json()["results"]

        orders = Order.objects.filter(user__in=users_filtered)
        items1 = OrderItem1.objects.filter(order__user__in=users_filtered).aggregate(
            sum=Coalesce(Sum("price"), Decimal("0.0")), count=Count("id")
        )

        items2 = OrderItem2.objects.filter(order__user__in=users_filtered).aggregate(
            sum=Coalesce(Sum(F("placement_price") + F("article_price")), Decimal("0.0")),
            count=Count("id")

        )
        expected_report = {
            "new_users": users_filtered.count(),
            "activated_users": users_filtered.count(),
            "orders_count": f"{orders.count()}",
            "orderitem1_count": items1["count"],
            "orderitem1_amount": f'{items1["sum"].quantize(Decimal("0.01"))}',
            "orderitem2_count": items2["count"],
            "orderitem2_amount": f'{items2["sum"].quantize(Decimal("0.01"))}',
        }
        actual_report = {
            "new_users": sum(r.new_users for r in report_rows),
            "activated_users": sum(r.new_users for r in report_rows),
            "orders_count": f"{sum(r.orders_count for r in report_rows)}",
            "orderitem1_count": sum(r.orderitem1_count for r in report_rows),
            "orderitem1_amount": f"{sum(r.orderitem1_amount for r in report_rows):.2f}",
            "orderitem2_count": sum(r.orderitem2_count for r in report_rows),
            "orderitem2_amount": f"{sum(r.orderitem2_amount for r in report_rows):.2f}",
        }
        response_report = {
            "new_users": sum(r["new_users"] for r in response_rows),
            "activated_users": sum(r["new_users"] for r in response_rows),
            "orders_count": f'{sum(r["orders_count"] for r in response_rows)}',
            "orderitem1_count": sum(r["orderitem1_count"] for r in response_rows),
            "orderitem1_amount": f'{sum(r["orderitem1_amount"] for r in response_rows):.2f}',
            "orderitem2_count": sum(r["orderitem2_count"] for r in response_rows),
            "orderitem2_amount": f'{sum(r["orderitem2_amount"] for r in response_rows):.2f}',
        }

        self.assertEqual(expected_report, response_report)
        self.assertEqual(actual_report, expected_report)

        print_report_by_rows(report_rows)

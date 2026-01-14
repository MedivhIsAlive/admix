from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, F, Q, Value, DecimalField
from django.db.models.functions import Coalesce, TruncDate, TruncWeek, TruncMonth
from django.utils import timezone

from orders.models import Order, OrderItem1, OrderItem2
from report.chrono import iter_period_starts

import enum


class Period(enum.StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "montly"


@dataclass()
class ReportRow:
    period: str
    new_users: int
    activated_users: int
    orders_count: int
    orderitem1_count: int
    orderitem1_amount: Decimal
    orderitem2_count: int
    orderitem2_amount: Decimal

    @property
    def orders_total_amount(self):
        return self.orderitem1_amount + self.orderitem2_amount


def generate_user_orders_report(
    start: date = None,
    end: date = None,
    period: Period = Period.WEEKLY,
) -> list[ReportRow]:
    if (end and start and (end < start)):
        raise ValueError("end must be >= start")
    if start is None:
        raise ValueError("start date is required")

    for (start, end) in iter_period_starts(
        start_date=start,
        end_date=end or timezone.now(),
    ):

        user_rows = (
            get_user_model()
            .objects
            .filter(
                date_joined__gte=start,
                date_joined__lt=end,
            )
            .with_stats()
        )
        money_zero = Value(Decimal("0.0"))
        report_data = user_rows.aggregate(
            new_users=Count("id"),
            activated_users=Count("id", filter=Q(is_active=True)),
            orders_count=Coalesce(Sum(user_rows.query.annotations["orders_count"]), 0),
            orderitem1_count=Coalesce(Sum(user_rows.query.annotations["items1_count"]), 0),
            orderitem1_amount=Coalesce(Sum(user_rows.query.annotations["items1_spent"]), money_zero),
            orderitem2_count=Coalesce(Sum(user_rows.query.annotations["items2_count"]), 0),
            orderitem2_amount=Coalesce(Sum(user_rows.query.annotations["items2_spent"]), money_zero),
        )
        yield ReportRow(
            period=f"{start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}",
            **report_data,
        )



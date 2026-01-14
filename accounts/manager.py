from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.db.models import Count, Sum, F, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce

from orders.models import Order, OrderItem1, OrderItem2


class UserQuerySet(models.QuerySet):

    def with_stats(self) -> "UserQuerySet":
        money_field = models.DecimalField(max_digits=18, decimal_places=2)
        zero_money = Value(0, output_field=money_field)

        orders_count_sq = (
            Order.objects
            .filter(user=OuterRef("pk"))
            .order_by()
            .values("user")
            .annotate(c=Count("id"))
            .values("c")
        )

        items1_base = (
            OrderItem1.objects
            .filter(order__user=OuterRef("pk"))
            .order_by()
            .values("order__user")
        )
        items1_count_sq = items1_base.annotate(c=Count("id")).values("c")
        items1_spent_sq = items1_base.annotate(s=Sum("price")).values("s")

        items2_base = (
            OrderItem2.objects
            .filter(order__user=OuterRef("pk"))
            .order_by()
            .values("order__user")
        )
        items2_count_sq = items2_base.annotate(c=Count("id")).values("c")
        items2_spent_sq = items2_base.annotate(
            s=Sum(F("placement_price") + F("article_price"))
        ).values("s")

        return self.annotate(
            orders_count=Coalesce(
                Subquery(orders_count_sq[:1], output_field=models.IntegerField()),
                Value(0)
            ),
            items1_count=Coalesce(
                Subquery(items1_count_sq[:1], output_field=models.IntegerField()),
                Value(0)
            ),
            items1_spent=Coalesce(
                Subquery(items1_spent_sq[:1], output_field=money_field),
                zero_money
            ),
            items2_count=Coalesce(
                Subquery(items2_count_sq[:1], output_field=models.IntegerField()),
                Value(0)
            ),
            items2_spent=Coalesce(
                Subquery(items2_spent_sq[:1], output_field=money_field),
                zero_money
            ),
        )


class UserManagerQS(BaseUserManager.from_queryset(UserQuerySet)):
    pass


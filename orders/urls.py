from django.urls import path
from orders.views import UserOrdersReportView

urlpatterns = [
    path("reports/user-orders/", UserOrdersReportView.as_view(), name="user-orders-report"),
]

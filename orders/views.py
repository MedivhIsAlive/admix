from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from report import generate_user_orders_report
from orders.serializers import ReportRequestSerializer


class UserOrdersReportView(APIView):
    def get(self, request):
        serializer = ReportRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        report_data = generate_user_orders_report(
            start=validated_data["start_date"],
            end=validated_data["end_date"],
            period=validated_data["period"],
        )

        paginator = PageNumberPagination()
        paginator.page_size = 50

        result = paginator.paginate_queryset([r.to_dict() for r in report_data], request)

        return paginator.get_paginated_response(result)


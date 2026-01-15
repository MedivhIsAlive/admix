from rest_framework import serializers
from report.period import Period


class ReportRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    period = serializers.ChoiceField(
        choices=[(p.value, p.name) for p in Period],
        default=Period.WEEKLY,
    )

    def validate(self, data):
        if data.get("end_date") and data.get("start_date"):
            if data["end_date"] < data["start_date"]:
                raise serializers.ValidationError(
                    {"end_date": "End date must be >= start_date."}
                )
        return super().validate(data)

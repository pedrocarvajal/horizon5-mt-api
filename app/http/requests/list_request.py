from rest_framework import serializers


def cast_filter_value(
    column: str,
    value: str,
    integer_columns: set[str],
    float_columns: set[str],
) -> int | float | str:
    try:
        if column in integer_columns:
            return int(value)
        if column in float_columns:
            return float(value)
    except ValueError:
        raise serializers.ValidationError({"filter_value": f"Invalid value '{value}' for column '{column}'."}) from None
    return value


class ListRequestSerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1, min_value=1)
    per_page = serializers.IntegerField(default=50, min_value=1, max_value=100)
    order_by = serializers.CharField(required=False, default="-created_at")
    filter_by = serializers.ChoiceField(choices=[], required=False)
    filter_value = serializers.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filterable_columns = self.context.get("filterable_columns", [])
        self.fields["filter_by"].choices = [(column, column) for column in filterable_columns]

    def validate_order_by(self, value: str) -> str:
        orderable_columns = self.context.get("orderable_columns", [])
        raw_column = value.lstrip("-")

        if raw_column not in orderable_columns:
            raise serializers.ValidationError(
                f"Invalid order_by column '{raw_column}'. Valid columns: {', '.join(orderable_columns)}"
            )

        return value

    def validate(self, attrs: dict) -> dict:
        filter_by = attrs.get("filter_by")
        filter_value = attrs.get("filter_value")

        if filter_by and not filter_value:
            raise serializers.ValidationError({"filter_value": "filter_value is required when filter_by is provided."})

        if filter_value and not filter_by:
            raise serializers.ValidationError({"filter_by": "filter_by is required when filter_value is provided."})

        return attrs

    def get_cast_filter_value(self, column: str, value: str) -> int | float | str:
        integer_columns = self.context.get("integer_columns", set())
        float_columns = self.context.get("float_columns", set())

        return cast_filter_value(column, value, integer_columns, float_columns)

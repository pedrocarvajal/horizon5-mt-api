from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=5, max_length=254, required=False)
    password = serializers.CharField(write_only=True, min_length=8, max_length=128, required=False)
    api_key = serializers.CharField(min_length=1, max_length=256, required=False, write_only=True)

    def validate(self, attrs):
        has_credentials = "email" in attrs and "password" in attrs
        has_api_key = "api_key" in attrs

        if has_credentials and has_api_key:
            raise serializers.ValidationError("Provide either email/password or api_key, not both.")

        if not has_credentials and not has_api_key:
            raise serializers.ValidationError("Provide email/password or api_key.")

        if has_credentials and ("email" not in attrs or "password" not in attrs):
            raise serializers.ValidationError("Both email and password are required.")

        return attrs

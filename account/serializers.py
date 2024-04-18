import re

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from account.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=20, min_length=8, write_only=True)

    def validate_password(self, value):
        # 비밀번호에 숫자, 문자, 특수문자를 모두 포함하는지 확인하는 정규 표현식
        if not re.match(r"^(?=.*\d)(?=.*[a-zA-Z])(?=.*[!@#$%^&*()-_+=]).*$", value):
            raise serializers.ValidationError("비밀번호는 숫자, 문자, 특수문자를 모두 포함해야 합니다.")
        return value

    def create(self, validated_data):
        # 비밀번호를 해시화하여 저장
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "profile_picture", "age", "password"]

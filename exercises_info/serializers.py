from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account.models import CustomUser as User
from exercises_info.models import ExercisesAttribute, ExercisesInfo, FocusArea
from utils.enums import FocusAreaEnum


class ExercisesAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExercisesAttribute
        fields = [
            "need_set",
            "need_rep",
            "need_weight",
            "need_duration",
            "need_speed",
        ]


class FocusAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusArea
        fields = ["focus_area"]

    def validate_focus_area(self, value):
        valid_focus_area_names = [enum.value for enum in FocusAreaEnum]
        if value not in valid_focus_area_names:
            raise ValidationError(f"{value} is not a valid focus area.")
        return value


class ExercisesInfoSerializer(WritableNestedModelSerializer):
    focus_areas = FocusAreaSerializer(many=True)
    exercises_attribute = ExercisesAttributeSerializer()
    username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = ExercisesInfo
        fields = [
            "id",
            "title",
            "author",
            "username",
            "description",
            "video",
            "focus_areas",
            "exercises_attribute",
        ]
        read_only_fields = ["id", "author", "username"]

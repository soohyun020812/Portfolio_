from django.utils import timezone
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from exercises_info.models import ExercisesInfo
from exercises_info.serializers import ExercisesInfoSerializer
from my_health_info.models import (
    ExerciseInRoutine,
    HealthInfo,
    MirroredRoutine,
    Routine,
    RoutineStreak,
    UsersRoutine,
    WeeklyRoutine,
    ExerciseInRoutineAttribute,
)


class HealthInfoSerializer(serializers.ModelSerializer):
    """
    사용자의 건강 정보를 다루는 Serializer
    """

    bmi = serializers.SerializerMethodField()

    class Meta:
        """
        HealthInfoSerializer의 Meta 클래스

        모델: HealthInfo

        필드:
        - user: 사용자, read_only
        - age: 나이
        - height: 키
        - weight: 몸무게
        - bmi: BMI, read_only
        """

        model = HealthInfo
        fields = ["user", "age", "height", "weight", "bmi", "date"]
        read_only_fields = ["user", "bmi", "created_at", "date"]

    def get_bmi(self, obj):
        """
        bmi를 계산하는 메서드
        """
        return round(obj.weight / ((obj.height / 100) ** 2), 2)

    def validate(self, data):
        """
        유효성 검사를 수행하는 메서드

        - 키와 몸무게가 양수인지 확인
        """

        if data["height"] <= 0:
            raise serializers.ValidationError("키는 양수여야 합니다.")
        if data["weight"] <= 0:
            raise serializers.ValidationError("몸무게는 양수여야 합니다.")
        return data


class ExerciseInRoutineAttributeSerializer(serializers.ModelSerializer):
    """
    ExerciseInRoutineSerializer에 사용되는 운동 정보 필드를 다루는 Serializer
    """

    class Meta:
        """
        ExerciseInRoutineAttribute의 Meta 클래스

        모델: ExerciseInRoutineAttribute

        필드:
        - exercise_in_routine: 가리키는 exercise_in_routine
        - set_count: 세트 수
        - rep_count: 반복 횟수
        - weight: 무게
        - duration: 시간
        - speed: 속도
        """

        model = ExerciseInRoutineAttribute
        fields = [
            "exercise_in_routine",
            "set_count",
            "rep_count",
            "weight",
            "duration",
            "speed",
        ]
        read_only_fields = ["exercise_in_routine"]

        def validate(self, data):
            if data.get("set_count") and data.get("set_count") < 0:
                raise serializers.ValidationError("세트 수는 0 이상이어야 합니다.")
            if data.get("rep_count") and data.get("rep_count") < 0:
                raise serializers.ValidationError("반복 횟수는 0 이상이어야 합니다.")
            if data.get("weight") and data.get("weight") < 0:
                raise serializers.ValidationError("무게는 0 이상이어야 합니다.")
            if data.get("duration") and data.get("duration") < 0:
                raise serializers.ValidationError("시간은 0 이상이어야 합니다.")
            if data.get("speed") and data.get("speed") < 0:
                raise serializers.ValidationError("속도는 0 이상이어야 합니다.")

            return data


class ExerciseInRoutineSerializer(WritableNestedModelSerializer):
    """
    루틴에 포함된 운동 정보를 다루는 Serializer
    """

    exercise_attribute = ExerciseInRoutineAttributeSerializer()

    class Meta:
        """
        ExerciseInRoutineSerializer의 Meta 클래스

        모델: ExerciseInRoutine

        필드:
        - routine: 루틴, read_only
        - exercise_info: 운동 정보
        - exercise: 운동 정보의 PK, write_only
        - order: 운동 순서
        """

        model = ExerciseInRoutine
        fields = [
            "routine",
            "mirrored_routine",
            "order",
            "exercise",
            "exercise_attribute",
        ]
        read_only_fields = ["routine", "mirrored_routine"]

    def validate(self, data):
        """
        유효성 검사를 수행하는 메서드

        - 운동 순서가 1 이상인지 확인
        """
        if data["order"] < 1:
            raise serializers.ValidationError("운동 순서는 1 이상이어야 합니다.")
        return data

    def to_representation(self, instance):
        """인스턴스를 반환하기 전에 호출되는 메서드, 커스텀 출력을 위해 오버라이드"""
        ret = super().to_representation(instance)

        ret["exercise"] = ExercisesInfoSerializer(instance.exercise).data
        import json

        return ret


class RoutineSerializer(WritableNestedModelSerializer):
    """
    Routine 모델을 위한 Serializer
    """

    username = serializers.SerializerMethodField()
    exercises_in_routine = ExerciseInRoutineSerializer(many=True)

    class Meta:
        """
        RoutineSerializer의 Meta 클래스

        모델: Routine

        필드:
        - author: 루틴 작성자
        - username: 루틴 작성자의 username
        - title: 루틴 제목
        - created_at: 루틴 생성일
        - is_deleted: 루틴 삭제 여부
        - like_count: 루틴 좋아요 수
        - exercises_in_routine: 루틴에 포함된 운동 정보
        """

        model = Routine
        fields = [
            "author",
            "username",
            "title",
            "created_at",
            "is_deleted",
            "like_count",
            "exercises_in_routine",
        ]
        read_only_fields = [
            "author",
            "username",
            "created_at",
            "is_deleted",
            "like_count",
        ]

    def get_username(self, obj):
        return obj.author.username


class MirroredRoutineSerializer(serializers.ModelSerializer):
    """
    MirroredRoutine 모델을 위한 Serializer
    """

    exercises_in_routine = ExerciseInRoutineSerializer(many=True)

    class Meta:
        """
        MirroredRoutineSerializer의 Meta 클래스

        모델: MirroredRoutine

        필드:
        - title: 루틴 제목, read_only
        - author_name: 루틴 작성자 이름, read_only
        - original_routine: 원본 루틴, read_only
        - exercises_in_routine: 루틴에 포함된 운동 정보, read_only, many
        """

        model = MirroredRoutine
        fields = ["title", "author_name", "original_routine", "exercises_in_routine"]
        read_only_fields = [
            "title",
            "author_name",
            "original_routine",
            "exercises_in_routine",
        ]


class UsersRoutineSerializer(serializers.ModelSerializer):
    """
    사용자의 루틴 정보를 다루는 Serializer
    """

    title = serializers.CharField(write_only=True)
    author = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    exercises_in_routine = ExerciseInRoutineSerializer(many=True, write_only=True)

    class Meta:
        """
        UsersRoutineSerializer의 Meta 클래스

        모델: UsersRoutine

        필드:
        - user: 사용자, read_only
        - routine: 루틴
        - mirrored_routine: 복제된 루틴
        - need_update: 업데이트 필요 여부
        """

        model = UsersRoutine
        fields = [
            "author",
            "author_name",
            "is_author",
            "title",
            "routine",
            "mirrored_routine",
            "exercises_in_routine",
            "need_update",
        ]
        read_only_fields = [
            "author",
            "is_author",
            "author_name",
            "routine",
            "mirrored_routine",
            "need_update",
        ]

    def validate(self, data):
        return data

    def get_author(self, obj):
        return obj.routine.author.id

    def get_author_name(self, obj):
        return obj.mirrored_routine.author_name

    def to_representation(self, instance):
        """인스턴스를 반환하기 전에 호출되는 메서드, 커스텀 출력을 위해 오버라이드"""
        ret = super().to_representation(instance)

        ret["title"] = (
            instance.mirrored_routine.title if instance.mirrored_routine else None
        )
        ret["exercises_in_routine"] = ExerciseInRoutineSerializer(
            instance.mirrored_routine.exercises_in_routine, many=True
        ).data

        return ret


class WeeklyRoutineSerializer(serializers.ModelSerializer):
    """
    주간 루틴 정보를 다루는 Serializer
    """

    class Meta:
        """
        WeeklyRoutineSerializer의 Meta 클래스

        모델: WeeklyRoutine

        필드:
        - user: 사용자, read_only
        - users_routine: 사용자의 루틴
        - day_index: 해당 루틴이 적용되는 요일 인덱스
        """

        model = WeeklyRoutine
        fields = ["user", "users_routine", "day_index"]
        read_only_fields = ["user"]

    def validate(self, data):
        """
        유효성 검사를 수행하는 메서드

        - day_index가 0~6 사이의 값인지 확인
        """

        if not 0 <= data["day_index"] <= 6:
            raise serializers.ValidationError("day_index는 0~6 사이의 값이어야 합니다.")
        return data


class RoutineStreakSerializer(serializers.ModelSerializer):
    """
    루틴 수행 여부를 다루는 Serializer
    """

    mirrored_routine = serializers.SerializerMethodField()

    class Meta:
        """
        RoutineStreakSerializer의 Meta 클래스

        모델: RoutineStreak

        필드:
        - id: 루틴 수행 여부의 PK, read_only
        - mirrored_routine: 수행된 복제된 루틴, read_only
        - date: 날짜, read_only
        """

        model = RoutineStreak
        fields = ["id", "mirrored_routine", "date"]
        read_only_fields = ["id", "mirrored_routine", "date"]

    def get_mirrored_routine(self, obj):
        try:
            weekly_routine = WeeklyRoutine.objects.get(
                day_index=obj.date.weekday(), user=obj.user
            )
        except WeeklyRoutine.DoesNotExist:
            raise serializers.ValidationError("해당 요일의 루틴이 존재하지 않습니다.")
        return weekly_routine.users_routine.mirrored_routine.id

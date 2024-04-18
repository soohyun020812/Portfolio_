import datetime

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import (
    MethodNotAllowed,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
from exercises_info.models import ExercisesInfo
from my_health_info.permissions import IsOwnerOrReadOnly
from my_health_info.serializers import (
    HealthInfoSerializer,
    RoutineSerializer,
    RoutineStreakSerializer,
    UsersRoutineSerializer,
    WeeklyRoutineSerializer,
    MirroredRoutineSerializer,
    ExerciseInRoutineSerializer,
)
from my_health_info.services import UsersRoutineManagementService


class MyHealthInfoViewSet(viewsets.ModelViewSet):
    """
    내 건강 정보에 대한 ViewSet

    url_prefix: /my_health_info/my_health_info/

    functions:
    - list: GET /my_health_info/my_health_info/
    - create: POST /my_health_info/my_health_info/
    - retrieve: GET /my_health_info/my_health_info/<pk>/
    - last: GET /my_health_info/my_health_info/last/
    """

    http_method_names = ["get", "post"]
    serializer_class = HealthInfoSerializer
    permission_classes = [IsAuthenticated]
    days_to_show = 35

    def get_queryset(self):
        """현재 유저의 건강 정보를 최신순으로 조회"""
        return HealthInfo.objects.filter(user=self.request.user).order_by("-date")

    def list(self, request, *args, **kwargs):
        """
        건강 정보를 리스트로 반환

        - 최근 35일간의 건강 정보만 조회 가능
        """
        queryset = (
            self.get_queryset()
            .all()
            .filter(
                date__gte=timezone.now() - datetime.timedelta(days=self.days_to_show)
            )
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        새로운 건강 정보 생성
        """
        if HealthInfo.objects.filter(
            user=self.request.user, date=datetime.datetime.now().date()
        ).exists():
            raise ValidationError("이미 오늘의 건강 정보가 등록되었습니다.")

        if serializer.is_valid():
            serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="last", url_name="last")
    def last(self, request, *args, **kwargs):
        """
        가장 최근의 건강 정보 조회

        사용자의 건강 정보가 없다면 404 에러 반환
        """
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        raise NotFound("No health info found")


class RoutineViewSet(viewsets.ModelViewSet):
    """
    루틴 정보에 대한 ViewSet

    url_prefix: /my_health_info/routine/

    functions:
    - list: GET /my_health_info/routine/
    - create: POST /my_health_info/routine/
    - subscribe: POST /my_health_info/routine/<pk>/subscribe/
    """

    http_method_names = [
        "get",
        "post",
    ]
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    ordering_fields = ["like_count"]

    def get_queryset(self):
        """
        루틴 정보를 반환, 삭제되지 않은 루틴만 조회
        """
        return Routine.objects.filter(is_deleted=False)

    def order_queryset(self, queryset):
        """
        주어진 쿼리셋을 ordering에 따라 정렬

        기본 ordering은 -created_at
        ordering이 없다면 기본 ordering을 사용

        추가 ordering은 query_params의 ordering 리스트 + 기본 ordering 순으로 배열
        그 후 order_by 함수를 사용하여 정렬
        """
        base_ordering = ["-created_at"]

        orderings = self.request.query_params.get("ordering", None)

        if not orderings:
            return queryset.order_by(*base_ordering)

        orderings = orderings.split(",")
        orderings = [
            ordering
            for ordering in orderings
            if ordering.lstrip("-") in self.ordering_fields
        ]
        orderings += base_ordering

        queryset = queryset.order_by(*orderings)

        return queryset

    def search_queryset(self, queryset):
        """
        주어진 쿼리셋을 검색어에 따라 필터링

        query_params의 search에 해당하는 필드를 검색어로 포함하는 루틴만 반환

        검색어가 없다면 주어진 쿼리셋 그대로 반환

        Q 객체를 사용하여 검색어에 해당하는 필드를 필터링
        """
        author__id = self.request.query_params.get("author__id", None)

        if not author__id:
            return queryset

        queryset = queryset.filter(Q(author__id=author__id))

        return queryset

    def list(self, request, *args, **kwargs):
        """
        루틴 정보를 리스트로 반환

        주어진 쿼리셋을 검색어와 ordering에 따라 필터링 및 정렬

        그 후 serializer를 사용하여 데이터 반환
        """
        queryset = self.get_queryset()
        queryset = self.search_queryset(queryset)
        queryset = self.order_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        특정 루틴 정보 조회

        주어진 pk에 해당하는 루틴 정보를 반환
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="like",
        url_name="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request, *args, **kwargs):
        routine = self.get_object()
        user = request.user

        if routine.liked_users.filter(id=user.id).exists():
            raise MethodNotAllowed("이미 좋아요를 누른 루틴입니다.")

        routine.liked_users.add(user)
        routine.like_count += 1

        return Response(
            data={"like_count": f"{routine.like_count}"}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, *args, **kwargs):
        """
        유저가 루틴을 구독하는 로직

        1. 루틴과 유저 인스턴스를 가져옴
        2. UsersRoutineManagementService를 통해 유저가 루틴을 구독하게 함
        3. 구독된 UsersRoutine을 반환
        """
        routine = self.get_object()
        user = request.user
        service = UsersRoutineManagementService(user=user, routine=routine)

        users_routine = service.user_subscribe_routine()

        data = UsersRoutineSerializer(users_routine).data

        return Response(data, status=status.HTTP_201_CREATED)


class UsersRoutineViewSet(viewsets.ModelViewSet):
    """
    유저의 루틴 정보에 대한 ViewSet

    url_prefix: /my_health_info/users_routine/

    functions:
    - list: GET /my_health_info/users_routine/
    - create: POST /my_health_info/users_routine/
    - retrieve: GET /my_health_info/users_routine/<pk>/
    - partial_update: PATCH /my_health_info/users_routine/<pk>/
    - destroy: DELETE /my_health_info/users_routine/<pk>/
    - update_routine: PATCH /my_health_info/users_routine/<pk>/update_routine/
    """

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = UsersRoutineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        본인이 소유한 루틴 정보를 반환
        """
        return UsersRoutine.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        유저가 소유한 UsersRoutine 정보를 리스트로 반환
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        새로운 UsersRoutine 생성

        1. 새 Routine 생성
        2. Routine을 original_routine으로 갖는 새 MirroredRoutine 생성
        3. 제공받은 ExerciseInRoutine 정보를 이용해 새 ExerciseInRoutine 생성
        4. 새 UsersRoutine 생성
        5. Serializer로 UsersRoutine 정보 반환
        """

        data = serializer.validated_data

        routine = Routine.objects.create(
            author=self.request.user,
            title=data["title"],
        )

        mirrored_routine = MirroredRoutine.objects.create(
            title=data["title"],
            author_name=self.request.user.username,
            original_routine=routine,
        )
        data.pop("title")
        exercises_in_routine = data["exercises_in_routine"]

        for exercise_in_routine in exercises_in_routine:

            exercises_in_routine_obj = ExerciseInRoutine.objects.create(
                routine=routine,
                mirrored_routine=mirrored_routine,
                exercise=exercise_in_routine["exercise"],
                order=exercise_in_routine["order"],
            )

            exercise_attr_request = exercise_in_routine.get("exercise_attribute", None)
            if exercise_attr_request:
                exercise = exercise_in_routine["exercise"]

                ExerciseInRoutineAttribute.objects.create(
                    exercise_in_routine=exercises_in_routine_obj,
                    set_count=(
                        exercise_attr_request["set_count"]
                        if exercise.exercises_attribute.need_set
                        else 0
                    ),
                    rep_count=(
                        exercise_attr_request["rep_count"]
                        if exercise.exercises_attribute.need_rep
                        else 0
                    ),
                    weight=(
                        exercise_attr_request["weight"]
                        if exercise.exercises_attribute.need_weight
                        else 0
                    ),
                    duration=(
                        exercise_attr_request["duration"]
                        if exercise.exercises_attribute.need_duration
                        else 0
                    ),
                    speed=(
                        exercise_attr_request["speed"]
                        if exercise.exercises_attribute.need_speed
                        else 0
                    ),
                )

        data.pop("exercises_in_routine")

        serializer.save(
            user=self.request.user,
            is_author=True,
            routine=routine,
            mirrored_routine=mirrored_routine,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        UsersRoutine 정보 업데이트

        1. UsersRoutine 정보를 가져옴
        2. 만약 ExercisesInRoutine 정보가 변경되어야 한다면
        3. Routine에 연결된 MirroredRoutine을 None으로 변경
        4. 새 MirroredRoutine 생성
        5. 기존 ExerciseInRoutine에서 routine 정보를 None으로 변경
        6. 새 ExerciseInRoutine 생성
        7. UsersRoutine의 mirrored_routine 정보를 새 MirroredRoutine으로 변경
        8. 만약 기존 MirroredRoutine의 구독자가 없다면 삭제
        9. UsersRoutine의 구독자에게 업데이트 필요 여부를 True로 변경
        """

        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        exercise_in_routine_data = data.pop("exercises_in_routine", None)

        routine = instance.routine
        if request.user != instance.routine.author:
            raise PermissionDenied("You are not the author of this routine")

        mirrored_routine = instance.mirrored_routine

        if "title" in data.keys():
            title = data["title"]

        if exercise_in_routine_data:
            mirrored_routine = routine.mirrored_routine
            mirrored_routine.original_routine = None
            mirrored_routine.save()
            routine.save()

            new_mirrored_routine = MirroredRoutine.objects.create(
                title=title,
                author_name=request.user.username,
                original_routine=routine,
            )

            existing_exercise_in_routines = instance.routine.exercises_in_routine.all()
            for exercise_in_routine in existing_exercise_in_routines:
                exercise_in_routine.routine = None
                exercise_in_routine.save()

            for exercise_in_routine in exercise_in_routine_data:

                exercises_in_routine_obj = ExerciseInRoutine.objects.create(
                    routine=routine,
                    mirrored_routine=new_mirrored_routine,
                    exercise=exercise_in_routine["exercise"],
                    order=exercise_in_routine["order"],
                )

                exercise_attr_request = exercise_in_routine.get(
                    "exercise_attribute", None
                )
                if exercise_attr_request:
                    exercise = exercise_in_routine["exercise"]

                    ExerciseInRoutineAttribute.objects.create(
                        exercise_in_routine=exercises_in_routine_obj,
                        set_count=(
                            exercise_attr_request["set_count"]
                            if exercise.exercises_attribute.need_set
                            else 0
                        ),
                        rep_count=(
                            exercise_attr_request["rep_count"]
                            if exercise.exercises_attribute.need_rep
                            else 0
                        ),
                        weight=(
                            exercise_attr_request["weight"]
                            if exercise.exercises_attribute.need_weight
                            else 0
                        ),
                        duration=(
                            exercise_attr_request["duration"]
                            if exercise.exercises_attribute.need_duration
                            else 0
                        ),
                        speed=(
                            exercise_attr_request["speed"]
                            if exercise.exercises_attribute.need_speed
                            else 0
                        ),
                    )

            instance.mirrored_routine = new_mirrored_routine
            instance.save()

            if mirrored_routine.mirrored_subscribers.count() == 0:
                mirrored_routine.delete()

            for subscriber in instance.routine.subscribers.all():
                if subscriber != instance:
                    subscriber.need_update = True
                    subscriber.save()

        routine.title = title
        routine.save()
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        UsersRoutine 정보 삭제

        1. UsersRoutine 정보를 가져옴
        2. UsersRoutine 정보 삭제
        3. 만약 유저가 루틴의 작성자라면 Routine 삭제
        4. 만약 MirroredRoutine의 구독자가 없다면 MirroredRoutine 삭제
        """
        instance = self.get_object()

        routine = instance.routine
        mirrored_routine = instance.mirrored_routine

        instance.delete()

        if request.user == instance.routine.author:
            routine.delete()

        if mirrored_routine.mirrored_subscribers.count() == 0:
            mirrored_routine.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class WeeklyRoutineView(APIView):
    """
    유저의 주간 루틴 정보에 대한 View

    url_prefix: /my_health_info/weekly_routine/

    functions:
    - get: GET /my_health_info/weekly_routine/
    - post: POST /my_health_info/weekly_routine/
    - update: PUT /my_health_info/weekly_routine/
    - delete: DELETE /my_health_info/weekly_routine/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        유저의 주간 루틴 정보 조회

        1. 쿼리셋에서 유저의 주간 루틴 정보를 조회하여 요일 순으로 정렬
        2. WeeklyRoutineSerializer를 사용하여 데이터 반환
        """
        user = request.user
        queryset = WeeklyRoutine.objects.filter(user=user).order_by("day_index")
        serializer = WeeklyRoutineSerializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request):
        """
        유저의 주간 루틴 정보 생성

        1. WeeklyRoutineSerializer를 사용하여 데이터 유효성 검사
        2. WeeklyRoutine들을 생성
        3. 생성된 WeeklyRoutine을 요일 순으로 정렬
        4. 정렬된 WeeklyRoutine을 WeeklyRoutineSerializer를 사용하여 데이터 반환
        """
        serializer = WeeklyRoutineSerializer(data=request.data, many=True)
        if serializer.is_valid():
            if WeeklyRoutine.objects.filter(user=request.user).exists():
                raise PermissionDenied("Weekly routine already exists")
            instances = serializer.save(user=request.user)
            sorted_instances = sorted(instances, key=lambda x: x.day_index)
            sorted_serializer = WeeklyRoutineSerializer(sorted_instances, many=True)
            return Response(sorted_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        유저의 주간 루틴 정보 업데이트

        1. WeeklyRoutineSerializer를 사용하여 데이터 유효성 검사
        2. instances에 유저의 주간 루틴 정보를 조회
        3. 현재 주간 루틴 정보의 요일 인덱스와 새로운 주간 루틴 정보의 요일 인덱스를 비교하여 삭제, 생성, 업데이트할 요일 인덱스 저장
        4. 업데이트 할 인덱스가 있다면 해당 인덱스의 users_routine 정보를 업데이트
        5. 삭제할 인덱스가 있다면 인덱스에 해당하는 주간 루틴 정보 삭제
        6. 생성할 인덱스가 있다면 인덱스에 해당하는 주간 루틴 정보 생성
        7. 업데이트된 주간 루틴 정보를 요일 순으로 정렬
        8. 정렬된 주간 루틴 정보를 WeeklyRoutineSerializer를 사용하여 데이터 반환
        """
        serializer = WeeklyRoutineSerializer(data=request.data, many=True)
        if serializer.is_valid():
            instances = WeeklyRoutine.objects.filter(user=request.user)

            current_indices = set(instance.day_index for instance in instances)
            new_indices = set(data["day_index"] for data in serializer.validated_data)

            to_delete = current_indices - new_indices
            to_create = new_indices - current_indices
            to_update = current_indices & new_indices

            if to_update:
                for data in serializer.validated_data:
                    if data["day_index"] in to_update:
                        WeeklyRoutine.objects.filter(
                            user=request.user, day_index=data["day_index"]
                        ).update(users_routine=data["users_routine"])
            if to_delete:
                WeeklyRoutine.objects.filter(
                    user=request.user, day_index__in=to_delete
                ).delete()
            if to_create:
                for data in serializer.validated_data:
                    if data["day_index"] in to_create:
                        WeeklyRoutine.objects.create(
                            user=request.user,
                            users_routine=data["users_routine"],
                            day_index=data["day_index"],
                        )

            instances = WeeklyRoutine.objects.filter(user=request.user)

            sorted_instances = sorted(instances, key=lambda x: x.day_index)
            sorted_serializer = WeeklyRoutineSerializer(sorted_instances, many=True)
            return Response(sorted_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        유저의 모든 주간 루틴 정보 삭제

        1. 유저의 주간 루틴 정보를 필터링하여 삭제
        2. 204 응답 반환
        """

        WeeklyRoutine.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoutineStreakViewSet(viewsets.ModelViewSet):
    """
    루틴 수행 여부를 나타내는 ViewSet

    url_prefix: /my_health_info/routine_streak/

    functions:
    - list: GET /my_health_info/routine_streak/
    - create: POST /my_health_info/routine_streak/
    - retrieve: GET /my_health_info/routine_streak/<pk>/
    """

    http_method_names = ["get", "post"]
    serializer_class = RoutineStreakSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        유저의 루틴 수행 여부를 반환
        """
        return RoutineStreak.objects.filter(user=self.request.user)

    def list(self, request):
        """
        루틴 수행 여부를 리스트로 반환

        1. 쿼리셋에서 유저의 루틴 수행 여부를 조회 후 날짜 역순으로 정렬
        2. serializer를 사용하여 데이터 반환
        """
        queryset = RoutineStreak.objects.filter(user=request.user).order_by("-date")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        루틴 수행 여부를 생성

        1. serializer에서 validated_data를 가져옴
        2. validated_data에서 user를 현재 유저로 설정
        3. RoutineStreak을 생성
        """
        validated_data = serializer.validated_data
        validated_data["user"] = self.request.user

        if RoutineStreak.objects.filter(
            user=self.request.user, date=datetime.datetime.now().date()
        ).exists():
            raise ValidationError("Routine streak already exists for today")

        serializer.save()

    @action(
        detail=False,
        methods=["get"],
        url_path="last",
        url_name="last",
        permission_classes=[IsAuthenticated],
    )
    def last(self, request):
        """
        가장 최근의 루틴 수행 여부 조회

        1. 쿼리셋에서 유저의 루틴 수행 여부를 조회 후 날짜 역순으로 정렬
        2. serializer를 사용하여 데이터 반환
        """
        queryset = RoutineStreak.objects.filter(user=request.user).order_by("-date")
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        raise NotFound("No routine streak found")

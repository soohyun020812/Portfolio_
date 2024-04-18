import json
import random
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import CustomUser as User
from exercises_info.models import ExercisesInfo
from my_health_info.models import (
    ExerciseInRoutine,
    HealthInfo,
    MirroredRoutine,
    Routine,
    RoutineStreak,
    UsersRoutine,
    WeeklyRoutine,
)
from my_health_info.services import UsersRoutineManagementService
from utils.fake_data import (
    FakeExerciseInRoutine,
    FakeExercisesInfo,
    FakeHealthInfo,
    FakeRoutine,
    FakeRoutineStreak,
    FakeUser,
    FakeWeeklyRoutine,
)


class MyHealthInfoTestCase(APITestCase):
    @freeze_time("2020-01-01")
    def setUp(self):
        """초기설정"""
        self.user1 = FakeUser()
        self.user1.create_instance()

        self.user1_health_info = FakeHealthInfo()
        self.user1_health_info.create_instance(user_instance=self.user1.instance)

    def calculate_users_bmi(self, health_info):
        """BMI 계산"""
        return round(
            health_info.get("weight") / ((health_info.get("height") / 100) ** 2), 2
        )

    def assert_equal_health_info(self, health_info, expected_health_info):
        """건강 정보 비교"""

        expected_health_info = expected_health_info.request_create()

        self.assertEqual(health_info.get("age"), expected_health_info.get("age"))
        self.assertEqual(health_info.get("height"), expected_health_info.get("height"))
        self.assertEqual(health_info.get("weight"), expected_health_info.get("weight"))
        self.assertEqual(
            health_info.get("bmi"),
            self.calculate_users_bmi(expected_health_info),
        )

    def test_get_my_health_info_not_authenticated(self):
        """비로그인 유저가 my-helath-info/에 접근할 때 401 에러를 리턴하는지 테스트"""
        new_health_info = FakeHealthInfo()
        new_health_info_request = new_health_info.request_create()

        responses = {
            "list": self.client.get(reverse("my-health-info-list")),
            "create": self.client.post(
                reverse("my-health-info-list"),
                data=new_health_info_request,
                content_type="application/json",
            ),
            "retrieve": self.client.get(
                reverse("my-health-info-detail", kwargs={"pk": 1})
            ),
            "put": self.client.put(
                reverse("my-health-info-detail", kwargs={"pk": 1}),
                data=new_health_info_request,
                content_type="application/json",
            ),
            "patch": self.client.patch(
                reverse("my-health-info-detail", kwargs={"pk": 1}),
                data=new_health_info_request,
                content_type="application/json",
            ),
            "delete": self.client.delete(
                reverse("my-health-info-detail", kwargs={"pk": 1})
            ),
            "last": self.client.get(reverse("my-health-info-last")),
        }

        for action, response in responses.items():
            with self.subTest(action=action):
                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                    f"{action} did not return 401",
                )

    def test_get_my_health_info_last_30_days(self):
        """로그인한 유저가 my-health-info-list에 접근할 때 최근 35일간의 건강 정보를 리턴하는지 테스트"""
        new_user = FakeUser()
        new_user.create_instance()

        now = timezone.now()
        for days_back in range(40, -1, -1):
            past_day = now - timedelta(days=days_back)
            with freeze_time(f"{past_day.strftime('%Y-%m-%d')}"):
                new_health_info = FakeHealthInfo()
                new_health_info.create_instance(user_instance=new_user.instance)

        new_user.login(self.client)

        response = self.client.get(reverse("my-health-info-list"))
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            len(data),
            HealthInfo.objects.filter(
                user=new_user.instance, date__gte=now - timedelta(days=35)
            ).count(),
        )

    def test_post_my_health_info(self):
        """POST 요청으로 건강 정보를 생성하는지 테스트"""
        self.user1.login(self.client)

        new_health_info = FakeHealthInfo()

        response = self.client.post(
            reverse("my-health-info-list"),
            data=json.dumps(new_health_info.request_create()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assert_equal_health_info(data, new_health_info)

    @freeze_time("2025-01-01")
    def test_reject_post_my_health_info_if_same_day(self):
        """POST 요청으로 같은 날짜에 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        new_health_info = FakeHealthInfo()

        self.user1.login(self.client)

        response_1 = self.client.post(
            reverse("my-health-info-list"),
            data=json.dumps(new_health_info.request_create()),
            content_type="application/json",
        )

        response_2 = self.client.post(
            reverse("my-health-info-list"),
            data=json.dumps(new_health_info.request_create()),
            content_type="application/json",
        )

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_my_health_info_last(self):
        """GET 요청으로 가장 최근 생성된 건강 정보를 조회하는지 테스트"""
        new_health_info = FakeHealthInfo()
        new_health_info.create_instance(user_instance=self.user1.instance)

        self.user1.login(self.client)

        response = self.client.get(reverse("my-health-info-last"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_equal_health_info(response.json(), new_health_info)

    def test_retrieve_my_health_info(self):
        """GET 요청으로 특정 건강 정보를 조회하는지 테스트"""
        self.user1.login(self.client)

        new_health_info = FakeHealthInfo()
        new_health_info.create_instance(user_instance=self.user1.instance)

        pk = new_health_info.instance.pk

        response = self.client.get(reverse("my-health-info-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assert_equal_health_info(response.json(), new_health_info)

    def test_post_my_health_info_with_invalid_age(self):
        """POST 요청으로 나이가 음수인 건강 정보를 생성할 때 400 에러를 리턴하는지 테스트"""
        self.user1.login(self.client)
        new_health_info = FakeHealthInfo()

        data = new_health_info.request_create()

        data.update({"age": -1})

        response = self.client.post(
            reverse("my-health-info-list"),
            data=json.dumps(data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_my_health_info_with_not_allowed_method(self):
        """허용되지 않은 메소드로 my-health-info/에 접근할 때 405 에러를 리턴하는지 테스트"""
        self.user1.login(self.client)

        health_info_first = HealthInfo.objects.first()
        pk = health_info_first.pk

        new_health_info = FakeHealthInfo()

        responses = {
            "put": self.client.put(
                reverse("my-health-info-detail", kwargs={"pk": pk}),
                data=new_health_info,
                content_type="application/json",
            ),
            "patch": self.client.patch(
                reverse("my-health-info-detail", kwargs={"pk": pk}),
                data=new_health_info,
                content_type="application/json",
            ),
            "delete": self.client.delete(
                reverse("my-health-info-detail", kwargs={"pk": pk})
            ),
        }

        for action, response in responses.items():
            with self.subTest(action=action):
                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                    f"{action} did not return 405",
                )


class RoutineTestCase(APITestCase):
    """
    목적: Routine 모델과 /routine/ API에 대한 테스트를 진행합니다.

    Test cases:
    1. 비로그인 유저가 /routine/에 접근할 때 401 에러를 리턴하는지 테스트
    2. 로그인한 유저가 /routine/에 접근할 때 유저의 루틴 정보를 조회하는지 테스트
    3. 허용되지 않은 메소드로 /routine/에 접근할 때 405 에러를 리턴하는지 테스트
    4. 루틴에 좋아요를 누르는 요청이 올바르게 처리되는지 테스트
    5. 루틴을 좋아요 순으로 정렬하여 조회할 수 있는지 테스트
    6. 이미 좋아요를 누른 루틴에 좋아요를 누르는 요청 시 405 에러를 리턴하는지 테스트
    7. 루틴 목록에서 제작자로 검색하여 조회할 수 있는지 테스트
    8. 비로그인 유저가 루틴에 좋아요를 누르는 요청이 401 에러를 리턴하는지 테스트
    """

    def setUp(self):
        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)

        self.user1 = FakeUser()
        self.user1.create_instance()

        self.user2 = FakeUser()
        self.user2.create_instance()

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(self.admin.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(self.admin.instance)

        self.exercise3 = FakeExercisesInfo()
        self.exercise3.create_instance(self.admin.instance)

        self.exercise4 = FakeExercisesInfo()
        self.exercise4.create_instance(self.admin.instance)

        self.exercise5 = FakeExercisesInfo()
        self.exercise5.create_instance(self.admin.instance)

        self.routine1 = FakeRoutine([self.exercise1, self.exercise2])
        self.routine1.create_instance(user_instance=self.user1.instance)

        self.routine2 = FakeRoutine([self.exercise3, self.exercise4, self.exercise5])
        self.routine2.create_instance(user_instance=self.user2.instance)

        self.routine3 = FakeRoutine([self.exercise4, self.exercise2, self.exercise3])
        self.routine3.create_instance(user_instance=self.user1.instance)

    def test_get_routine_not_authenticated(self):
        """
        비로그인 유저가 /routine/에 접근할 때 401 에러를 리턴하는지 테스트

        reverse_url: routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 비로그인 유저가 /routine/에 GET 요청을 보냅니다.
        2. 403 에러를 리턴하는지 확인합니다.
        """
        response = self.client.get(reverse("routine-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_routine_authenticated(self):
        """
        로그인한 유저가 /routine/에 접근할 때 루틴들을 조회하는지 테스트

        reverse_url: routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 로그인한 유저가 /routine/에 GET 요청을 보냅니다.
        2. 현재 생성된 루틴들을 조회하는지 확인합니다.
        """
        routines_count = Routine.objects.count()

        self.user1.login(self.client)

        response = self.client.get(reverse("routine-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), routines_count)

    def test_request_routine_not_allowed_method(self):
        """
        허용되지 않은 메소드로 /routine/에 접근할 때 405 에러를 리턴하는지 테스트

        reverse_url: routine-detail
        HTTP method: PUT

        테스트 시나리오:
        1. 로그인한 유저가 /routine/에 PUT, PATCH, DELETE 요청을 보냅니다.
        2. 405 에러를 리턴하는지 확인합니다.
        """
        self.user1.login(self.client)

        pk = self.routine1.instance.pk

        put_response = self.client.put(reverse("routine-detail", kwargs={"pk": pk}))
        patch_response = self.client.patch(reverse("routine-detail", kwargs={"pk": pk}))
        delete_response = self.client.delete(
            reverse("routine-detail", kwargs={"pk": pk})
        )

        self.assertEqual(put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            delete_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_like_routine(self):
        """
        루틴에 좋아요를 누르는 요청이 올바르게 처리되는지 테스트

        reverse_url: routine-like
        HTTP method: POST

        테스트 시나리오:
        1. 로그인한 유저가 /routine/<pk>/like/에 POST 요청을 보냅니다.
        2. 루틴에 좋아요가 추가되었는지 확인합니다.
        """
        self.user1.login(self.client)

        like_count = self.routine2.instance.like_count

        pk = self.routine2.instance.pk

        response = self.client.post(reverse("routine-like", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertTrue(data.get("like_count"), like_count + 1)

    def test_like_routine_already_liked(self):
        """
        이미 좋아요를 누른 루틴에 좋아요를 누르는 요청이 올바르게 처리되는지 테스트

        reverse_url: routine-like
        HTTP method: POST

        테스트 시나리오:
        1. 로그인한 유저가 /routine/<pk>/like/에 POST 요청을 두 번 보냅니다.
        2. 405 에러를 리턴하는지 확인합니다.
        """
        self.user1.login(self.client)

        pk = self.routine2.instance.pk

        self.client.post(reverse("routine-like", kwargs={"pk": pk}))
        response = self.client.post(reverse("routine-like", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_routine_sorted_by_like(self):
        """
        루틴을 좋아요 순으로 정렬하여 조회할 수 있는지 테스트

        reverse_url: routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 새로운 유저 몇 명을 생성합니다.
        2. 새로운 루틴 몇 개를 생성합니다.
        3. 기존 루틴과 새로운 루틴에 좋아요 수를 변경합니다.
        4. 루틴을 좋아요 순으로 정렬합니다.
        5. /routine/에 GET 요청을 보냅니다.
        6. Response의 루틴들이 정렬해둔 루틴의 좋아요와 일치하는지 확인합니다.
        """
        new_user_1 = FakeUser()
        new_user_1.create_instance()

        new_user_2 = FakeUser()
        new_user_2.create_instance()

        new_user_3 = FakeUser()
        new_user_3.create_instance()

        new_routine_1 = FakeRoutine([self.exercise1, self.exercise2])
        new_routine_1.create_instance(user_instance=new_user_1.instance)

        new_routine_2 = FakeRoutine([self.exercise3, self.exercise4])
        new_routine_2.create_instance(user_instance=new_user_2.instance)

        new_routine_1.instance.like_count = 10
        new_routine_1.instance.save()

        new_routine_2.instance.like_count = 5
        new_routine_2.instance.save()

        sorted_routines = Routine.objects.all().order_by("-like_count")

        self.user1.login(self.client)

        response = self.client.get(reverse("routine-list") + "?ordering=-like_count")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        for routine_instances, response_routine in zip(sorted_routines, data):
            self.assertEqual(
                routine_instances.like_count, response_routine.get("like_count")
            )

    def test_search_routine_by_author(self):
        """
        루틴 목록에서 제작자로 검색하여 조회할 수 있는지 테스트

        reverse_url: routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 로그인한 유저가 /routine/에 GET 요청을 보냅니다.
        2. Response의 루틴들이 로그인한 유저가 생성한 루틴들만 조회되는지 확인합니다.
        """

        self.user1.login(self.client)

        response = self.client.get(
            reverse("routine-list") + f"?author__id={self.user1.instance.id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        for routine in data:
            self.assertEqual(routine.get("username"), self.user1.instance.username)

    def test_like_routine_not_authenticated(self):
        """
        비로그인 유저가 루틴에 좋아요를 누르는 요청이 401 에러를 리턴하는지 테스트

        reverse_url: routine-like
        HTTP method: POST

        테스트 시나리오:
        1. 비로그인 유저가 /routine/<pk>/like/에 POST 요청을 보냅니다.
        2. 401 에러를 리턴하는지 확인합니다.
        """
        pk = self.routine2.instance.pk

        response = self.client.post(reverse("routine-like", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ExerciseInRoutineTestCase(APITestCase):
    """
    목적: Routine 모델과 연결되어 루틴에 포함된 운동들을 관리하는 ExerciseInRoutine 모델에 대한 테스트를 진행합니다.

    Test cases:
    1. 루틴을 조회할 때 루틴에 포함된 운동들을 함께 조회하는지 테스트
    2. 루틴을 생성할 때 주어진 운동에 대한 정보를 함께 생성하는지 테스트
    3. 루틴을 업데이트할 때 주어진 운동에 대한 정보를 함께 업데이트하는지 테스트
    4. 루틴을 삭제할 때 함께 생성된 운동에 대한 정보도 함께 삭제하는지 테스트
    """

    def setUp(self):
        """
        초기 설정

        1. 어드민 유저 생성
        2. 운동을 5 개 생성
        3. 유저 2 명 생성
        4. 유저 1과 2가 각각 루틴을 생성
        """
        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(self.admin.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(self.admin.instance)

        self.exercise3 = FakeExercisesInfo()
        self.exercise3.create_instance(self.admin.instance)

        self.exercise4 = FakeExercisesInfo()
        self.exercise4.create_instance(self.admin.instance)

        self.exercise5 = FakeExercisesInfo()
        self.exercise5.create_instance(self.admin.instance)

        self.user1 = FakeUser()
        self.user1.create_instance()

        self.routine1 = FakeRoutine([self.exercise1, self.exercise2, self.exercise3])
        self.routine1.create_instance(user_instance=self.user1.instance)

        self.user2 = FakeUser()
        self.user2.create_instance()

        self.routine2 = FakeRoutine([self.exercise4, self.exercise5])
        self.routine2.create_instance(user_instance=self.user2.instance)

    def test_get_exercise_in_ExerciseInRoutine(self):
        """
        루틴을 조회할 때 루틴에 포함된 운동들을 함께 조회하는지 테스트

        reverse_url: routine-detail
        HTTP method: GET

        테스트 시나리오:
        1. routine1에 포함된 운동들을 조회합니다.
        2. 그 수를 확인하고 배열에 저장합니다.
        3. /routine/<pk>/에 GET 요청을 보냅니다.
        4. Response의 운동들 수가 같은지 확인합니다.
        5. 미리 저장한 배열과 Response의 운동들이 같은지 확인합니다.
        """
        self.user.login(self.client)

        pk = self.routine1.instance.pk

        exercises = self.routine1.instance.exercises_in_routine.all()
        exercise_count = exercises.count()

        response = self.client.get(reverse("routine-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertTrue(len(data.get("exercises_in_routine")), exercise_count)
        for exercise, response_exercise in zip(
            exercises, data.get("exercises_in_routine")
        ):
            self.assertEqual(
                exercise.exercise.title,
                response_exercise.get("exercise_info").get("title"),
            )

    def test_create_exercise_in_ExerciseInRoutine(self):
        """
        루틴을 생성할 때 주어진 운동에 대한 정보를 함께 생성하는지 테스트

        reverse_url: routine-list
        HTTP method: POST

        테스트 시나리오:
        1. 새로운 운동을 생성합니다.
        2. 새로운 루틴을 생성하고 생성된 운동들을 루틴에 추가합니다.
        3. /routine/에 POST 요청을 보냅니다.
        4. Response의 운동들이 생성된 운동들과 같은지 확인합니다.
        """
        new_exercise1 = FakeExercisesInfo()
        new_exercise1.create_instance(self.admin.instance)

        new_exercise2 = FakeExercisesInfo()
        new_exercise2.create_instance(self.admin.instance)

        new_routine = FakeRoutine([new_exercise1, new_exercise2])

        new_exercises_in_routine = new_routine.related_fake_models.get(
            "exercises_in_routine"
        )

        self.user1.login(self.client)

        response = self.client.post(
            reverse("routine-list"),
            data=new_routine.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        for exercise, response_exercise in zip(
            new_exercises_in_routine, data.get("exercises_in_routine")
        ):
            self.assertEqual(
                exercise.related_fake_models.get("exercises_info").instance.title,
                response_exercise.get("exercise_info").get("title"),
            )

    def test_update_exercise_in_ExerciseInRoutine(self):
        """
        루틴을 업데이트할 때 주어진 운동에 대한 정보를 함께 업데이트하는지 테스트

        reverse_url: routine-detail
        HTTP method: PATCH

        테스트 시나리오:
        1. 새로운 운동을 생성합니다.
        2. 새 운동에 대한 정보와 순서가 담긴 ExerciseInRoutine 배열을 생성합니다.
        3. /routine/<pk>/에 PATCH 요청을 보냅니다.
        4. Response의 운동들이 예상한 운동들과 같은지 확인합니다.
        """
        new_exercise1 = FakeExercisesInfo()
        new_exercise1.create_instance(self.admin.instance)

        new_exercise2 = FakeExercisesInfo()
        new_exercise2.create_instance(self.admin.instance)

        new_exercise_in_routine1 = FakeExerciseInRoutine(
            order=1, fake_exercises_info=new_exercise1
        )
        new_exercise_in_routine2 = FakeExerciseInRoutine(
            order=2, fake_exercises_info=new_exercise2
        )

        existed_exercise_in_routines = self.routine1.instance.exercises_in_routine.all()

        request_update = [
            new_exercise_in_routine1.request_create(),
            new_exercise_in_routine2.request_create(),
        ]

        pk = self.routine1.instance.pk

        self.user1.login(self.client)

        response = self.client.patch(
            reverse("routine-detail", kwargs={"pk": pk}),
            data={"exercises_in_routine": request_update},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        for exercise, response_exercise in zip(
            request_update, data.get("exercises_in_routine")
        ):
            self.assertEqual(
                ExercisesInfo.objects.get(pk=exercise.get("exercise")).title,
                response_exercise.get("exercise_info").get("title"),
            )

    def test_delete_exercise_in_ExerciseInRoutine(self):
        """
        루틴을 삭제할 때 함께 생성된 운동에 대한 정보는 삭제되지 않는지 테스트

        reverse_url: routine-detail
        HTTP method: DELETE

        테스트 시나리오:
        1. routine1에 포함된 운동들을 조회합니다.
        2. 그 id를 배열에 저장합니다.
        3. /routine/<pk>/에 DELETE 요청을 보냅니다.
        4. response가 204를 리턴하는지 확인합니다.
        5. 해당 루틴이 삭제되었는지 확인합니다.
        6. 해당 루틴 내의 운동이 삭제되지 않았는지 확인합니다.
        7. 해당 루틴 내의 운동들이 삭제되지 않았는지 확인합니다.
        """
        self.user1.login(self.client)

        pk = self.routine1.instance.pk

        exercise_in_routines = self.routine1.instance.exercises_in_routine.all()
        exercise_in_routine_ids = [
            exercise_in_routine.pk for exercise_in_routine in exercise_in_routines
        ]
        exercise_ids = [
            exercise_in_routine.exercise.pk
            for exercise_in_routine in exercise_in_routines
        ]

        response = self.client.delete(reverse("routine-detail", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Routine.objects.filter(pk=pk).exists())

        for id in exercise_in_routine_ids:
            self.assertTrue(ExerciseInRoutine.objects.filter(pk=id).exists())

        for id in exercise_ids:
            self.assertTrue(ExercisesInfo.objects.filter(pk=id).exists())


class UsersRoutineTestCase(APITestCase):
    """
    목적: 유저가 보유한 루틴을 관리하는 UsersRoutine 모델에 대한 테스트를 진행합니다.

    Test cases:
    1. 유저가 보유한 루틴을 조회하는지 테스트
    2. 유저가 UsersRoutine을 생성할 때 Routine이 함께 생성되는지 테스트
    3. 유저가 루틴을 구독했을 시 UsersRoutine이 생성되는지 테스트
    4. 유저가 생성한 루틴이 업데이트되었을 시 작성자와 구독자의 SideEffect가 제대로 작동하는지 테스트
    5. 유저가 자신이 작성한 UsersRoutine을 삭제했을때 SideEffect가 잘 작동하는지 테스트
    6. 유저가 구독중인 UsersRoutine을 삭제했을 시 SideEffect가 잘 작동했는지 테스트
    """

    def setUp(self):
        """
        초기 설정

        1. 관리자 유저 생성
        2. 운동 4개 생성
        3. 유저 2명 생성
        4. 유저 1이 루틴 1개 생성
        5. 유저 2가 루틴 1개 생성
        6. 유저 1이 유저 2의 루틴을 구독
        7. 유저 2가 유저 1의 루틴을 구독
        """
        self.client = APIClient()

        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(self.admin.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(self.admin.instance)

        self.exercise3 = FakeExercisesInfo()
        self.exercise3.create_instance(self.admin.instance)

        self.exercise4 = FakeExercisesInfo()
        self.exercise4.create_instance(self.admin.instance)

        self.user1 = FakeUser()
        self.user1.create_instance()

        self.routine1 = FakeRoutine([self.exercise1, self.exercise2])
        self.routine1.create_instance(user_instance=self.user1.instance)

        self.user2 = FakeUser()
        self.user2.create_instance()

        self.routine2 = FakeRoutine([self.exercise3, self.exercise4])
        self.routine2.create_instance(user_instance=self.user2.instance)

        self.routine3 = FakeRoutine([self.exercise1, self.exercise2])
        self.routine3.create_instance(user_instance=self.user2.instance)

        service = UsersRoutineManagementService(
            routine=self.routine2.instance, user=self.user1.instance
        )

        self.user1_routine_written_by_user2 = service.user_subscribe_routine()

        service = UsersRoutineManagementService(
            routine=self.routine1.instance, user=self.user2.instance
        )
        self.user2_routine_written_by_user1 = service.user_subscribe_routine()

    def test_get_users_routine(self):
        """
        유저가 보유한 루틴을 조회하는지 테스트

        reverse_url: routine-users-routine-list
        HTTP method: GET

        테스트 시나리오:
        1. 유저 1이 보유한 루틴을 조회합니다.
        2. 그 수를 확인하고 배열에 저장합니다.
        3. /users-routine/에 GET 요청을 보냅니다.
        4. Response의 루틴들 수가 같은지 확인합니다.
        5. 미리 저장한 배열과 Response의 루틴들이 같은지 확인합니다.
        """
        self.user1.login(self.client)

        user1_routines = UsersRoutine.objects.filter(user=self.user1.instance)

        routine_count = user1_routines.count()

        response = self.client.get(reverse("users-routine-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), routine_count)
        for user1_routine, response_routine in zip(user1_routines, data):
            self.assertEqual(user1_routine.routine.id, response_routine.get("routine"))

    def test_create_routine_when_create_users_routine(self):
        """
        유저가 새 UsersRoutine을 생성할 때 Routine이 함께 생성되는지 테스트

        reverse_url: users-routine-list
        HTTP method: POST

        테스트 시나리오:
        1. Routine의 개수를 저장합니다.
        2. 유저 2가 로그인합니다.
        3. users-routine-list에 post 요청을 보냅니다.
        4. 응답 코드가 201인지 확인합니다.
        5. Routine의 개수가 1 증가했는지 확인합니다.
        6. 가장 최근에 생성된 UsersRoutine의 정보와 응답 데이터의 정보를 비교합니다.
        """

        routine_count = Routine.objects.count()

        new_routine = FakeRoutine([self.exercise1, self.exercise2])

        self.user2.login(self.client)

        response = self.client.post(
            reverse("users-routine-list"),
            data=json.dumps(new_routine.request_create()),
            content_type="application/json",
        )

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Routine.objects.count(), routine_count + 1)

    def test_create_users_routine_when_subscribe_routine(self):
        """
        유저가 루틴을 구독했을 시 UsersRoutine이 생성되는지 테스트

        reverse_url: routine-subscribe
        HTTP method: POST

        테스트 시나리오:
        1. 유저 2로 로그인합니다.
        2. 유저 1이 생성한 루틴을 구독합니다.
        3. 응답 코드가 201인지 확인합니다.
        4. 구독한 루틴이 응답 데이터에 포함된 루틴과 같은지 확인합니다.
        """
        pk = self.routine3.instance.pk

        self.user1.login(self.client)

        response = self.client.post(reverse("routine-subscribe", kwargs={"pk": pk}))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(self.routine3.instance.pk, data.get("routine"))

    def test_update_users_routine_if_author(self):
        """
        유저가 생성한 루틴이 업데이트되었을 시 SideEffect가 제대로 작동하는지 테스트

        reverse_url: users-routine-detail
        HTTP method: PATCH

        테스트 시나리오:
        1. 유저 1이 로그인합니다.
        2. 유저 1이 생성한 UsersRoutine을 업데이트합니다.
        3. 응답 코드가 200인지 확인합니다.
        4. Routine의 정보가 업데이트되었는지 확인합니다.
        5. 업데이트된 Routine의 mirrored_routine이 UsersRoutine의 mirrored_routine과 같은지 확인합니다.
        6. UsersRoutine의 need_update가 False인지 확인합니다.
        7. 유저 2의 users_routine을 비교해서 mirrored_routine이 응답 데이터와 다른지 확인합니다.
        8. 유저 2의 users_routine의 need_update가 True인지 확인합니다.
        """

        self.user1.login(self.client)

        user1_routine = UsersRoutine.objects.filter(user=self.user1.instance).first()
        user2_routine = UsersRoutine.objects.filter(
            user=self.user2.instance, routine=user1_routine.routine
        ).first()

        pk = user1_routine.pk

        new_routine = FakeRoutine([self.exercise3, self.exercise4])

        response = self.client.patch(
            reverse("users-routine-detail", kwargs={"pk": pk}),
            data=json.dumps(new_routine.request_create()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user1_routine.refresh_from_db()
        user2_routine.refresh_from_db()

        data = response.json()
        print(json.dumps(data, indent=2))
        self.assertEqual(
            user1_routine.mirrored_routine.id, data.get("mirrored_routine")
        )
        self.assertEqual(user1_routine.routine.id, data.get("routine"))
        self.assertEqual(new_routine.base_attr.get("title"), data.get("title"))
        self.assertFalse(data.get("need_update"))

        self.assertNotEqual(
            user2_routine.mirrored_routine.id, data.get("mirrored_routine")
        )
        self.assertTrue(user2_routine.need_update)

    def test_delete_users_routine_if_author(self):
        """
        유저가 자신이 작성한 UsersRoutine을 삭제했을때 SideEffect가 잘 작동하는지 테스트

        reverse_url: users-routine-detail
        HTTP method: DELETE

        테스트 시나리오:
        1. 유저 1이 로그인합니다.
        2. 유저 1이 생성한 UsersRoutine을 삭제합니다.
        3. 응답 코드가 204인지 확인합니다.
        4. UsersRoutine이 삭제되었는지 확인합니다.
        5. 기존에 UsersRoutine과 연결된 Routine이 삭제되었는지 확인합니다.
        6. UsersRoutine에 연결됬던 MirroredRoutine이 삭제되지 않았는지 확인합니다.
        """

        self.user1.login(self.client)

        user1_routine = UsersRoutine.objects.filter(user=self.user1.instance).first()
        user1_routine_routine_pk = user1_routine.routine.pk
        user1_routine_mirrored_routine_pk = user1_routine.mirrored_routine.pk

        pk = user1_routine.pk

        response = self.client.delete(
            reverse("users-routine-detail", kwargs={"pk": pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(UsersRoutine.objects.filter(pk=pk).exists())
        self.assertFalse(Routine.objects.filter(pk=user1_routine_routine_pk).exists())
        self.assertTrue(
            MirroredRoutine.objects.filter(
                pk=user1_routine_mirrored_routine_pk
            ).exists()
        )

    def test_delete_users_routine_if_not_author(self):
        """
        구독중인 UsersRoutine을 삭제했을 시 SideEffect가 잘 작동하는지 테스트

        reverse_url: users-routine-detail
        HTTP method: DELETE

        테스트 시나리오:
        1. 유저 1이 구독중인 user1_routine_written_by_user2를 삭제합니다.
        2. 응답 코드가 204인지 확인합니다.
        3. UsersRoutine이 삭제되었는지 확인합니다.
        4. Routine이 삭제되지 않았는지 확인합니다.
        5. MirroredRoutine이 삭제되지 않았는지 확인합니다.
        """

        self.user1.login(self.client)

        pk = self.user1_routine_written_by_user2.pk

        response = self.client.delete(
            reverse("users-routine-detail", kwargs={"pk": pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(UsersRoutine.objects.filter(pk=pk).exists())
        self.assertTrue(Routine.objects.filter(pk=self.routine2.instance.pk).exists())
        self.assertTrue(
            MirroredRoutine.objects.filter(
                pk=self.routine2.instance.mirrored_routine.pk
            ).exists()
        )


class WeeklyRoutineTestCase(APITestCase):
    """
    목적: 유저의 한 주에 대한 루틴을 관리하는 WeeklyRoutine 모델에 대한 테스트를 진행합니다.

    Test cases:
    1. 유저가 현재 설정된 주간 루틴을 조회하는지 테스트
    2. 유저가 새로운 정보로 주간 루틴을 생성하는지 테스트
    3. 이미 루틴을 생성한 유저가 새로운 정보로 주간 루틴을 생성에 실패하는지 테스트
    4. 잘못된 day_index가 포함된 request로 주간 루틴을 생성에 실패하는지 테스트
    5. 유저가 주간 루틴을 변경하는것에 성공하는지 테스트
    6. 유저가 주간 루틴을 삭제하는것에 성공하는지 테스트
    """

    def setUp(self):
        """
        초기 설정:

        1. 관리자 유저 생성
        2. 운동 5개 생성
        3. 유저 1 생성
        4. 유저 1이 루틴 4개 생성
        """
        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(self.admin.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(self.admin.instance)

        self.exercise3 = FakeExercisesInfo()
        self.exercise3.create_instance(self.admin.instance)

        self.exercise4 = FakeExercisesInfo()
        self.exercise4.create_instance(self.admin.instance)

        self.exercise5 = FakeExercisesInfo()
        self.exercise5.create_instance(self.admin.instance)

        self.user1 = FakeUser()
        self.user1.create_instance()

        self.routine1 = FakeRoutine([self.exercise1, self.exercise2])
        self.routine1.create_instance(user_instance=self.user1.instance)

        self.routine2 = FakeRoutine([self.exercise3, self.exercise4])
        self.routine2.create_instance(user_instance=self.user1.instance)

        self.routine3 = FakeRoutine([self.exercise1, self.exercise5])
        self.routine3.create_instance(user_instance=self.user1.instance)

        self.routine4 = FakeRoutine([self.exercise2, self.exercise3])
        self.routine4.create_instance(user_instance=self.user1.instance)

    def test_get_weekly_routine(self):
        """
        유저가 현재 설정된 주간 루틴을 조회하는지 테스트

        reverse_url: weekly-routine
        HTTP method: GET

        테스트 시나리오:
        1. 유저 1이 현재 생성된 루틴으로 WeeklyRoutine 인스턴스를 생성합니다.
        2. 유저 1이 로그인합니다.
        3. /weekly-routine/에 GET 요청을 보냅니다.
        4. 상태 코드가 200인지 확인합니다.
        5. 응답의 길이를 확인합니다.
        6. 응답의 WeeklyRoutine의 id가 유저 1이 생성한 루틴의 id와 같은지 확인합니다.
        7. 응답의 WeeklyRoutine들의 day_index가 유저 1이 생성한 WeeklyRoutine들의 day_index 순서와 같은지 확인합니다.
        """

        user1_users_routine_instances = [
            self.routine3.instance.subscribers.get(user=self.user1.instance),
            self.routine2.instance.subscribers.get(user=self.user1.instance),
            self.routine4.instance.subscribers.get(user=self.user1.instance),
            self.routine1.instance.subscribers.get(user=self.user1.instance),
        ]

        random_day_indices = [0, 5, 3, 2]

        fake_weekly_routines = [
            FakeWeeklyRoutine(
                day_index=random_day_index, users_routine=users_routine_instance
            )
            for random_day_index, users_routine_instance in zip(
                random_day_indices, user1_users_routine_instances
            )
        ]

        for fake_weekly_routine in fake_weekly_routines:
            fake_weekly_routine.create_instance(user_instance=self.user1.instance)

        self.user1.login(self.client)

        response = self.client.get(reverse("weekly-routine"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), len(fake_weekly_routines))

        for fake_weekly_routine, response_weekly_routine in zip(
            sorted(fake_weekly_routines, key=lambda x: x.instance.day_index), data
        ):
            self.assertEqual(
                fake_weekly_routine.instance.users_routine.id,
                response_weekly_routine.get("users_routine"),
            )
            self.assertEqual(
                fake_weekly_routine.instance.day_index,
                response_weekly_routine.get("day_index"),
            )

    def test_create_weekly_routine_if_weekly_routines_empty(self):
        """
        주간 루틴을 보유하지 않은 유저가 새로운 정보로 주간 루틴을 생성하는지 테스트

        reverse_url: weekly-routine
        HTTP method: POST

        테스트 시나리오:
        1. 새로운 FakeWeeklyRoutine 배열을 생성합니다.
        2. 유저 1이 로그인합니다.
        3. /weekly-routine/에 POST 요청을 보냅니다.
        4. 상태 코드가 201인지 확인합니다.
        5. 응답의 길이를 확인합니다.
        6. 응답의 각 WeeklyRoutine의 day_index가 생성한 FakeWeeklyRoutine의 day_index와 같은지 확인합니다.
        7. 응답의 각 WeeklyRoutine의 users_routine이 생성한 FakeWeeklyRoutine의 users_routine과 같은지 확인합니다.
        """
        user1_users_routine_instances = [
            self.routine3.instance.subscribers.get(user=self.user1.instance),
            self.routine2.instance.subscribers.get(user=self.user1.instance),
            self.routine4.instance.subscribers.get(user=self.user1.instance),
            self.routine1.instance.subscribers.get(user=self.user1.instance),
        ]

        random_day_indices = [0, 5, 3, 2]

        fake_weekly_routines = [
            FakeWeeklyRoutine(
                day_index=random_day_index, users_routine=users_routine_instance
            )
            for random_day_index, users_routine_instance in zip(
                random_day_indices, user1_users_routine_instances
            )
        ]

        self.user1.login(self.client)

        create_request = [
            fake_weekly_routine.create_request()
            for fake_weekly_routine in fake_weekly_routines
        ]

        response = self.client.post(
            reverse("weekly-routine"),
            data=json.dumps(create_request),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(len(data), len(fake_weekly_routines))

        for fake_weekly_routine, response_weekly_routine in zip(
            sorted(fake_weekly_routines, key=lambda x: x.base_attr.get("day_index")),
            data,
        ):
            self.assertEqual(
                fake_weekly_routine.users_routine.id,
                response_weekly_routine.get("users_routine"),
            )
            self.assertEqual(
                fake_weekly_routine.base_attr.get("day_index"),
                response_weekly_routine.get("day_index"),
            )

    def test_fail_create_weekly_routine_if_weekly_routines_existed(self):
        """
        이미 루틴을 보유한 유저가 새로운 정보로 주간 루틴을 생성하는것을 실패하는지 테스트

        reverse_url: weekly-routine
        HTTP method: POST

        테스트 시나리오:
        1. 유저 1이 현재 생성된 루틴으로 WeeklyRoutine 인스턴스를 생성합니다.
        2. 새로운 FakeWeeklyRoutine 배열을 생성합니다.
        3. 유저 1이 로그인합니다.
        4. /weekly-routine/에 POST 요청을 보냅니다.
        5. 상태 코드가 403인지 확인합니다.
        """

        user1_users_routine_instances = [
            self.routine3.instance.subscribers.get(user=self.user1.instance),
            self.routine2.instance.subscribers.get(user=self.user1.instance),
            self.routine4.instance.subscribers.get(user=self.user1.instance),
            self.routine1.instance.subscribers.get(user=self.user1.instance),
        ]

        random_day_indices1 = [1, 3, 5, 2]

        fake_weekly_routines1 = [
            FakeWeeklyRoutine(
                day_index=random_day_index, users_routine=users_routine_instance
            )
            for random_day_index, users_routine_instance in zip(
                random_day_indices1, user1_users_routine_instances
            )
        ]

        for fake_weekly_routine in fake_weekly_routines1:
            fake_weekly_routine.create_instance(user_instance=self.user1.instance)

        random_day_indices2 = [6, 1, 4, 2]

        fake_weekly_routines2 = [
            FakeWeeklyRoutine(
                day_index=random_day_index, users_routine=users_routine_instance
            )
            for random_day_index, users_routine_instance in zip(
                random_day_indices2, user1_users_routine_instances
            )
        ]

        create_request = [
            fake_weekly_routine.create_request()
            for fake_weekly_routine in fake_weekly_routines2
        ]

        self.user1.login(self.client)

        response = self.client.post(
            reverse("weekly-routine"),
            data=json.dumps(create_request),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fail_create_weekly_routine_if_invalid_day_index(self):
        """
        잘못된 day_index가 포함된 request로 주간 루틴을 생성에 실패하는지 테스트

        reverse_url: weekly-routine
        HTTP method: POST

        테스트 시나리오:
        1. WeeklyRoutine의 개수를 저장합니다.
        2. 잘못된 day_index가 포함된 새로운 FakeWeeklyRoutine 배열을 생성합니다.
        3. 유저 1이 로그인합니다.
        4. /weekly-routine/에 POST 요청을 보냅니다.
        5. 상태 코드가 400인지 확인합니다.
        6. WeeklyRoutine의 개수가 변하지 않았는지 확인합니다.
        """

        weekly_routine_count = WeeklyRoutine.objects.count()

        user1_users_routine_instances = [
            self.routine3.instance.subscribers.get(user=self.user1.instance),
            self.routine2.instance.subscribers.get(user=self.user1.instance),
            self.routine4.instance.subscribers.get(user=self.user1.instance),
            self.routine1.instance.subscribers.get(user=self.user1.instance),
        ]

        wrong_day_indices = [0, 8, 3, 2]

        self.user1.login(self.client)

        create_request = [
            FakeWeeklyRoutine(
                day_index=wrong_day_index, users_routine=users_routine_instance
            ).create_request()
            for wrong_day_index, users_routine_instance in zip(
                wrong_day_indices, user1_users_routine_instances
            )
        ]

        response = self.client.post(
            reverse("weekly-routine"),
            data=create_request,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(WeeklyRoutine.objects.count(), weekly_routine_count)

    def test_update_weekly_routine(self):
        """
        유저가 주간 루틴을 변경하는것에 성공하는지 테스트

        reverse_url: weekly-routine
        HTTP method: PUT

        테스트 시나리오:
        1. 유저 1이 현재 생성된 루틴으로 WeeklyRoutine 인스턴스를 생성합니다.
        2. 새로운 FakeWeeklyRoutine 배열을 생성합니다.
        3. 유저 1이 로그인합니다.
        4. /weekly-routine/에 PUT 요청을 보냅니다.
        5. 상태 코드가 200인지 확인합니다.
        6. 응답의 길이가 기존 WeeklyRoutine의 수와 다른지 확인합니다.
        7. 응답의 길이가 새로운 FakeWeeklyRoutine 배열의 길이와 같은지 확인합니다.
        8. day_index를 비교하여 변경이 잘 처리되었는지 확인합니다.
        """

        user1_users_routine_instances = [
            self.routine3.instance.subscribers.get(user=self.user1.instance),
            self.routine2.instance.subscribers.get(user=self.user1.instance),
            self.routine4.instance.subscribers.get(user=self.user1.instance),
            self.routine1.instance.subscribers.get(user=self.user1.instance),
        ]

        random_day_indices1 = [1, 3, 5, 2]

        fake_weekly_routines1 = [
            FakeWeeklyRoutine(
                day_index=random_day_index, users_routine=users_routine_instance
            )
            for random_day_index, users_routine_instance in zip(
                random_day_indices1, user1_users_routine_instances
            )
        ]

        for fake_weekly_routine in fake_weekly_routines1:
            fake_weekly_routine.create_instance(user_instance=self.user1.instance)

        new_user1_users_routine_instances = [
            self.routine1.instance.subscribers.get(user=self.user1.instance),
            self.routine4.instance.subscribers.get(user=self.user1.instance),
            self.routine2.instance.subscribers.get(user=self.user1.instance),
        ]

        random_day_indices2 = [1, 5, 4]

        fake_weekly_routines2 = [
            FakeWeeklyRoutine(
                day_index=random_day_index, users_routine=users_routine_instance
            )
            for random_day_index, users_routine_instance in zip(
                random_day_indices2, new_user1_users_routine_instances
            )
        ]

        self.user1.login(self.client)

        put_request = [
            fake_weekly_routine.create_request()
            for fake_weekly_routine in fake_weekly_routines2
        ]

        response = self.client.put(
            reverse("weekly-routine"),
            data=json.dumps(put_request),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertNotEqual(len(data), len(fake_weekly_routines1))
        self.assertEqual(len(data), len(fake_weekly_routines2))

        self.assertEqual(WeeklyRoutine.objects.count(), len(fake_weekly_routines2))

        for response_weekly_routine, fake_weekly_routine in zip(
            data,
            sorted(fake_weekly_routines2, key=lambda x: x.base_attr.get("day_index")),
        ):
            self.assertEqual(
                response_weekly_routine.get("day_index"),
                fake_weekly_routine.base_attr.get("day_index"),
            )
            self.assertEqual(
                response_weekly_routine.get("users_routine"),
                fake_weekly_routine.users_routine.id,
            )

    def test_delete_weekly_routine(self):
        """
        WeeklyRoutine에 대한 delete 테스트

        reverse_url: weekly-routine
        HTTP method: DELETE

        테스트 시나리오:
        1. 유저 1이 현재 생성된 루틴으로 WeeklyRoutine 인스턴스를 생성합니다.
        2. 유저 1이 로그인합니다.
        3. /weekly-routine/에 DELETE 요청을 보냅니다.
        4. 상태 코드가 204인지 확인합니다.
        5. 유저 1이 보유한 WeeklyRoutine이 모두 삭제되었는지 확인합니다.
        """

        user1_users_routine_instances = [
            self.routine3.instance.subscribers.get(user=self.user1.instance),
            self.routine2.instance.subscribers.get(user=self.user1.instance),
            self.routine4.instance.subscribers.get(user=self.user1.instance),
            self.routine1.instance.subscribers.get(user=self.user1.instance),
        ]

        random_day_indices = [1, 3, 5, 2]

        fake_weekly_routines = [
            FakeWeeklyRoutine(
                day_index=random_day_index, users_routine=users_routine_instance
            )
            for random_day_index, users_routine_instance in zip(
                random_day_indices, user1_users_routine_instances
            )
        ]

        for fake_weekly_routine in fake_weekly_routines:
            fake_weekly_routine.create_instance(user_instance=self.user1.instance)

        self.user1.login(self.client)

        response = self.client.delete(reverse("weekly-routine"))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            WeeklyRoutine.objects.filter(user=self.user1.instance).exists()
        )


class RoutineStreakTestCase(TestCase):
    """
    목적: 유저의 루틴 수행 기록을 관리하는 RoutineStreak 모델에 대한 테스트를 진행합니다.

    Test cases:
    1. 유저가 루틴을 수행한 기록을 조회하는지 테스트
    2. 유저가 특정 날짜에 수행한 기록의 세부 정보를 조회하는지 테스트
    3. 유저가 루틴을 수행한 기록을 생성하는지 테스트
    4. 유저가 이미 루틴을 수행한 상태에서 루틴을 수행한 기록을 생성하려 할 때 실패하는지 테스트
    5. 유저가 루틴이 등록되지 않은 요일에 루틴을 수행한 기록을 생성하려 할 때 실패하는지 테스트
    6. 최근 수행 루틴을 조회하는지 테스트
    7. 허용되지 않은 요청으로 접근 시 405 에러를 반환하는지 테스트
    """

    def setUp(self):
        """
        초기 설정:

        1. 관리자 유저 생성
        2. 운동 4개 생성
        3. 유저 1 생성
        4. 유저 1이 루틴 5개 생성
        5. 유저 1은 해당 루틴들로 WeeklyRoutine 생성
        6. freezegun을 사용해서 과거에서부터 루틴 수행 기록을 생성
        """

        self.client = APIClient()

        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)

        self.exercises = [FakeExercisesInfo() for _ in range(4)]
        for exercise in self.exercises:
            exercise.create_instance(self.admin.instance)

        self.user1 = FakeUser()
        self.user1.create_instance()

        refresh = RefreshToken.for_user(self.user1.instance)
        self.access_token = str(refresh.access_token)

        self.routines = [
            FakeRoutine([self.exercises[0], self.exercises[1]]),
            FakeRoutine([self.exercises[1], self.exercises[2]]),
            FakeRoutine([self.exercises[2], self.exercises[3], self.exercises[0]]),
            FakeRoutine([self.exercises[3]]),
            FakeRoutine([self.exercises[0], self.exercises[1], self.exercises[2]]),
        ]

        for routine in self.routines:
            routine.create_instance(user_instance=self.user1.instance)

        user1_users_routine_instances = [
            routine.instance.subscribers.get(user=self.user1.instance)
            for routine in self.routines
        ]

        self.random_day_indices = [6, 2, 1, 4]

        self.fake_weekly_routines = [
            FakeWeeklyRoutine(
                day_index=random_day_index, users_routine=users_routine_instance
            )
            for random_day_index, users_routine_instance in zip(
                self.random_day_indices, user1_users_routine_instances
            )
        ]

        for fake_weekly_routine in self.fake_weekly_routines:
            fake_weekly_routine.create_instance(user_instance=self.user1.instance)

        days = 30
        start_time = datetime.now() - timedelta(days=days)
        for i in range(days - 1):
            with freeze_time(start_time + timedelta(days=i)):
                day_index = datetime.now().weekday()

                if day_index in self.random_day_indices:
                    if random.random() < 0.6:
                        routine_streak = FakeRoutineStreak(
                            mirrored_routine=self.fake_weekly_routines[
                                self.random_day_indices.index(day_index)
                            ].users_routine.mirrored_routine,
                        )
                        routine_streak.create_instance(
                            user_instance=self.user1.instance
                        )

    def test_get_routine_streak_list(self):
        """
        유저가 루틴을 수행한 기록을 조회하는지 테스트

        reverse_url: routine-streak-list
        HTTP method: GET

        테스트 시나리오:
        1. 유저 1이 로그인합니다.
        2. /routine-streak/에 GET 요청을 보냅니다.
        3. 상태 코드가 200인지 확인합니다.
        4. 응답의 길이가 생성된 RoutineStreak의 수와 같은지 확인합니다.
        5. 응답의 RoutineStreak의 mirrored_routine이 생성된 RoutineStreak의 mirrored_routine과 같은지 확인합니다.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.get(reverse("routine-streak-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            RoutineStreak.objects.filter(user=self.user1.instance).count(), len(data)
        )

        for routine_streak in RoutineStreak.objects.filter(user=self.user1.instance):
            self.assertEqual(
                routine_streak.mirrored_routine.id, data.pop().get("mirrored_routine")
            )

    def test_get_routine_streak_detail(self):
        """
        유저가 특정 날짜에 수행한 기록의 세부 정보를 조회하는지 테스트

        reverse_url: routine-streak-detail
        HTTP method: GET

        테스트 시나리오:
        1. 유저 1이 로그인합니다.
        2. /routine-streak/에 GET 요청을 보냅니다.
        3. 상태 코드가 200인지 확인합니다.
        4. 응답의 날짜가 요청한 날짜와 같은지 확인합니다.
        5. 응답의 mirrored_routine이 요청한 mirrored_routine과 같은지 확인합니다.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        routine_streak = RoutineStreak.objects.filter(user=self.user1.instance).last()

        response = self.client.get(
            reverse("routine-streak-detail", kwargs={"pk": routine_streak.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(routine_streak.date.strftime("%Y-%m-%d"), data.get("date"))

        self.assertEqual(
            routine_streak.mirrored_routine.id, data.get("mirrored_routine")
        )

    def test_create_routine_streak(self):
        """
        유저가 루틴을 수행한 기록을 생성하는지 테스트

        reverse_url: routine-streak-list
        HTTP method: POST

        테스트 시나리오:
        1. 유저 1이 로그인합니다.
        2. /routine-streak/에 POST 요청을 보냅니다.
        3. 상태 코드가 201인지 확인합니다.
        4. 응답에 포함된 date가 현재 날짜와 같은지 확인합니다.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(
            reverse("routine-streak-list"),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(datetime.now().strftime("%Y-%m-%d"), data.get("date"))

    def test_create_routine_streak_fail_if_already_done(self):
        """
        유저가 이미 루틴을 수행한 상태에서 루틴을 수행한 기록을 생성하려 할 때 실패하는지 테스트

        reverse_url: routine-streak-list
        HTTP method: POST

        테스트 시나리오:
        1. 루틴을 수행한 기록을 생성합니다.
        2. 유저 1이 로그인합니다.
        3. /routine-streak/에 POST 요청을 보냅니다.
        4. 상태 코드가 400인지 확인합니다.
        """

        now_day_index = datetime.now().weekday()

        RoutineStreak.objects.create(
            user=self.user1.instance,
            mirrored_routine=self.fake_weekly_routines[
                self.random_day_indices.index(now_day_index)
            ].users_routine.mirrored_routine,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(
            reverse("routine-streak-list"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time(datetime.now() + timedelta(days=1))
    def test_create_routine_streak_fail_if_invalid_day_index(self):
        """
        유저가 루틴이 등록되지 않은 요일에 루틴을 수행한 기록을 생성하려 할 때 실패하는지 테스트

        reverse_url: routine-streak-list
        HTTP method: POST

        테스트 시나리오:
        1. 유저 1이 로그인합니다.
        2. /routine-streak/에 POST 요청을 보냅니다.
        3. 상태 코드가 400인지 확인합니다.
        """
        new_access_token = str(RefreshToken.for_user(self.user1.instance).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")

        response = self.client.post(
            reverse("routine-streak-list"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_last_routine_streak(self):
        """
        최근 수행 루틴을 조회하는지 테스트

        reverse_url: routine-streak-last
        HTTP method: GET

        테스트 시나리오:
        1. 유저 1이 로그인합니다.
        2. /routine-streak-last/에 GET 요청을 보냅니다.
        3. 상태 코드가 200인지 확인합니다.
        4. 응답의 date가 RoutineStreak.objects.last().date와 같은지 확인합니다.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.get(reverse("routine-streak-last"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            RoutineStreak.objects.filter(user=self.user1.instance)
            .last()
            .date.strftime("%Y-%m-%d"),
            data.get("date"),
        )

    def test_get_errors_when_not_allowed_methods(self):
        """
        허용되지 않은 요청으로 접근 시 405 에러를 반환하는지 테스트

        reverse_url: routine-streak-list, routine-streak-detail, routine-streak-last
        HTTP method: POST, PUT, PATCH, DELETE

        테스트 시나리오:
        1. 유저 1이 로그인합니다.
        2. /routine-streak-list, /routine-streak-detail, /routine-streak-last에 POST, PUT, PATCH, DELETE 요청을 보냅니다.
        3. 상태 코드가 405인지 확인합니다.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        routine_streak = RoutineStreak.objects.filter(user=self.user1.instance).last()

        response = self.client.put(
            reverse("routine-streak-detail", kwargs={"pk": routine_streak.id})
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(
            reverse("routine-streak-detail", kwargs={"pk": routine_streak.id})
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(
            reverse("routine-streak-detail", kwargs={"pk": routine_streak.id})
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

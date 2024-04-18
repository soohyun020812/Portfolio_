from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from account.models import CustomUser as User
from exercises_info.models import ExercisesAttribute, ExercisesInfo
from utils.fake_data import FakeExercisesInfo, FakeUser
import json


class ExercisesInfoTestCase(APITestCase):
    """
    목적: ExercisesInfo App의 API 테스트

    Test cases:
    1. 모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인
    2. 모든 사용자가 운동 정보 상세 페이지를 볼 수 있는지 확인
    3. 관리자만 운동 정보를 생성할 수 있는지 확인
    4. 일반유저가 운동 정보를 생성할 수 있는지 확인
    5. 관리자만 운동 정보를 수정할 수 있는지 확인
    6. 일반유저가 운동 정보를 수정할 수 있는지 확인
    7. 관리자만 운동 정보를 삭제할 수 있는지 확인
    8. 일반유저가 운동 정보를 삭제할 수 있는지 확인
    9. 운동 정보 생성 시 필수 필드가 누락되었을 때 에러가 발생하는지 확인
    10. Enum에 존재하지 않는 Focus Area를 입력했을 때 에러가 발생하는지 확인
    11. Focus Area의 수정 요청이 올바르게 처리되는지 확인
    12. Title의 길이가 100자를 초과했을 때 에러가 발생하는지 확인
    13. Description의 길이가 1000자를 초과했을 때 에러가 발생하는지 확인
    """

    def setUp(self):
        """
        사전 설정

        1. 관리자 계정 생성
        2. 일반 사용자 계정 생성
        3. 관리자 계정으로 운동 정보 2개 생성
        """
        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)

        self.user = FakeUser()
        self.user.create_instance()

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(user_instance=self.admin.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(user_instance=self.admin.instance)

    def test_all_users_can_view_exercises_list(self):
        """
        모든 사용자가 운동 정보 리스트를 볼 수 있는지 확인

        reverse_url : exercises-info-list
        HTTP method : GET

        테스트 시나리오:
        1. 서버에 GET 요청을 보냄
        3. 응답 코드가 200인지 확인
        4. 응답 데이터의 길이가 저장된 운동 정보 리스트의 요소 개수와 같은지 확인
        """
        exercise_count = ExercisesInfo.objects.count()

        response = self.client.get(reverse("exercises-info-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), exercise_count)

    def test_all_users_can_retrieve_exercise_detail(self):
        """
        모든 사용자가 운동 정보 상세 페이지를 볼 수 있는지 확인

        reverse_url : exercises-info-detail
        HTTP method : GET

        테스트 시나리오:
        1. 서버에 첫 번째로 생성한 운동 정보의 id로 GET 요청을 보냄
        2. 응답 코드가 200인지 확인
        3. 응답 데이터에 id에 해당하는 운동 정보의 제목이 있는지 확인
        """

        response = self.client.get(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.exercise1.instance.title)

    def test_admin_can_create_exercise(self):
        """
        관리자만 운동 정보를 생성할 수 있는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 새로운 운동 정보 생성
        3. 응답 코드가 201인지 확인
        4. 응답 데이터에 생성한 운동 정보의 제목이 있는지 확인
        """
        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(new_exercise.request_create()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        self.assertEqual(data["title"], new_exercise.request_create()["title"])

    def test_user_can_create_exercise(self):
        """
        일반유저가 운동 정보를 생성하려고 시도할 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 일반 유저 계정으로 로그인
        2. 서버에 POST 요청을 보내서 새로운 운동 정보 생성
        3. 응답 코드가 403인지 확인
        """
        new_exercise = FakeExercisesInfo()

        self.user.login(self.client)

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(new_exercise.request_create()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_exercise(self):
        """
        관리자만 운동 정보를 수정할 수 있는지 확인

        reverse_url : exercises-info-detail
        HTTP method : PATCH

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 PATCH 요청을 보내서 운동 정보 수정
        4. 응답 코드가 200인지 확인
        """
        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        response = self.client.patch(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
            data=json.dumps(new_exercise.request_create()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ExercisesInfo.objects.get(id=self.exercise1.instance.id).title,
            new_exercise.request_create()["title"],
        )

    def test_user_can_update_exercise(self):
        """
        일반유저가 운동 정보를 수정하려고 시도할 때 에러가 발생하는지 확인

        reverse_url : exercises-info-detail
        HTTP method : PATCH

        테스트 시나리오:
        1. 일반 유저 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 PATCH 요청을 보내서 운동 정보 수정
        4. 응답 코드가 403인지 확인
        """
        new_exercise = FakeExercisesInfo()

        self.user.login(self.client)

        response = self.client.patch(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
            data=json.dumps(new_exercise.request_create()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_exercise(self):
        """
        관리자만 운동 정보를 삭제할 수 있는지 확인

        reverse_url : exercises-info-detail
        HTTP method : DELETE

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 DELETE 요청을 보내서 운동 정보 삭제
        3. 응답 코드가 204인지 확인
        """
        self.admin.login(self.client)

        response = self.client.delete(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_can_delete_exercise(self):
        """
        일반유저가 운동 정보를 삭제하려고 시도할 때 에러가 발생하는지 확인

        reverse_url : exercises-info-detail
        HTTP method : DELETE

        테스트 시나리오:
        1. 일반 유저 계정으로 로그인
        2. 서버에 DELETE 요청을 보내서 운동 정보 삭제
        3. 응답 코드가 403인지 확인
        """
        self.user.login(self.client)
        response = self.client.delete(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ExercisesInfo.objects.count(), 2)

    def test_exercise_create_error_when_required_field_is_missing(self):
        """
        운동 정보 생성 시 필수 필드가 누락되었을 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 필수 필드가 누락된 상태로 운동 정보 생성
        3. 응답 코드가 400인지 확인
        """
        self.admin.login(self.client)
        response = self.client.post(
            reverse("exercises-info-list"),
            data={},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_exercise_create_error_when_focus_area_is_not_in_enum(self):
        """
        Enum에 존재하지 않는 Focus Area를 입력했을 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 Enum에 존재하지 않는 Focus Area를 입력한 상태로 운동 정보 생성
        3. 응답 코드가 400인지 확인
        """
        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()

        request_data["focus_areas"] = [
            {
                "focus_area": "test",
            }
        ]

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(request_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_focus_areas_successsfully(self):
        """
        Focus Area의 수정 요청이 올바르게 처리되는지 확인

        reverse_url : exercises-info-detail
        HTTP method : PATCH

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 PATCH 요청을 보내서 Focus Area 수정
        4. 응답 코드가 200인지 확인
        """
        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        response = self.client.patch(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
            data=json.dumps(
                {"focus_areas": new_exercise.request_create().get("focus_areas")}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        focus_areas = data.get("focus_areas")

        self.assertEqual(focus_areas, new_exercise.request_create().get("focus_areas"))

    def test_title_length_error(self):
        """
        Title의 길이가 100자를 초과했을 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 Title의 길이가 100자를 초과한 상태로 운동 정보 생성
        3. 응답 코드가 400인지 확인
        """
        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()
        request_data["title"] = "a" * 101

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(request_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_description_length_error(self):
        """
        Description의 길이가 1000자를 초과했을 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 서버에 POST 요청을 보내서 Description의 길이가 1000자를 초과한 상태로 운동 정보 생성
        3. 응답 코드가 400인지 확인
        """
        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()
        request_data["description"] = "a" * 1001

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(request_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ExercisesAttributeTestCase(APITestCase):
    """
    목적: ExercisesInfo App의 ExercisesInfo Model에서 OneToOneField로 연결된 ExercisesAttribute Model의 API 테스트

    Test cases:
    1. 생성된 운동 정보의 id로 연결된 ExercisesAttribute를 조회할 수 있는지 확인
    2. 새로운 운동 정보를 생성할 때 ExercisesAttribute가 제대로 생성되는지 확인
    3. 새로운 운동 정보를 생성할 때 ExercisesAttribute를 함께 생성하지 않으면 에러가 발생하는지 확인
    4. 새로운 운동 정보를 생성할 때 ExercisesAttribute의 필수 필드가 누락되었을 때 해당 필드가 False로 생성되는지 확인
    5. bool 이외의 타입으로 ExercisesAttribute 필드를 생성하려고 시도할 때 에러가 발생하는지 확인
    6. ExercisesInfo 수정 시 ExercisesAttribute도 함께 수정되는지 확인
    7. ExercisesInfo 삭제 시 ExercisesAttribute도 함께 삭제되는지 확인
    """

    def setUp(self):
        self.admin = FakeUser()
        self.admin.create_instance(is_staff=True)

        self.user = FakeUser()
        self.user.create_instance()

        self.exercise1 = FakeExercisesInfo()
        self.exercise1.create_instance(user_instance=self.admin.instance)

        self.exercise2 = FakeExercisesInfo()
        self.exercise2.create_instance(user_instance=self.admin.instance)

    def test_retrieve_exercise_attribute(self):
        """
        기존에 생성된 운동 정보의 id로 연결된 ExercisesAttribute를 조회할 수 있는지 확인

        reverse_url : exercises-info-detail
        HTTP method : GET

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 생성된 운동 정보의 id로 GET 요청을 보냄
        3. 응답 코드가 200인지 확인
        4. 응답 데이터에 ExercisesAttribute의 길이가 미리 정의된 값과 같은지 확인
        5. 응답 데이터에 ExercisesAttribute의 필드 값이 모두 정의된 값과 같은지 확인
        """

        self.admin.login(self.client)

        id = self.exercise1.instance.id

        exercises_attribute = self.exercise1.request_create().get("exercises_attribute")

        response = self.client.get(reverse("exercises-info-detail", kwargs={"pk": id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        data_exercises_attribute = data.get("exercises_attribute")

        self.assertEqual(len(data_exercises_attribute), len(exercises_attribute))

        for attr in exercises_attribute:
            self.assertEqual(
                data_exercises_attribute.get(attr), exercises_attribute.get(attr)
            )

    def test_create_exercise_with_exercises_attribute(self):
        """
        새로운 운동 정보를 생성할 때 ExercisesAttribute가 제대로 생성되는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 POST 요청을 보내서 새로운 운동 정보 생성
        4. 응답 코드가 201인지 확인
        5. 응답 데이터에 ExercisesAttribute의 필드 값이 모두 정의된 값과 같은지 확인
        """

        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(new_exercise.request_create()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        exercises_attribute = new_exercise.request_create().get("exercises_attribute")

        data_exercises_attribute = data.get("exercises_attribute")

        for attr in exercises_attribute:
            self.assertEqual(
                data_exercises_attribute.get(attr), exercises_attribute.get(attr)
            )

    def test_create_exercise_without_exercises_attribute(self):
        """
        새로운 운동 정보를 생성할 때 ExercisesAttribute를 함께 생성하지 않으면 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 POST 요청을 보내서 ExercisesAttribute를 함께 생성하지 않은 상태로 운동 정보 생성
        4. 응답 코드가 400인지 확인
        """

        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()
        del request_data["exercises_attribute"]

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(request_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_exercise_with_missing_exercises_attribute_fields(self):
        """
        새로운 운동 정보를 생성할 때 ExercisesAttribute의 필수 필드가 누락되었을 때 해당 필드가 False로 생성되는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 POST 요청을 보내서 ExercisesAttribute의 필수 필드가 누락된 상태로 운동 정보 생성
        4. 응답 코드가 201인지 확인
        5. 응답 데이터에 ExercisesAttribute의 필드 값이 모두 False인지 확인
        """

        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()
        del request_data["exercises_attribute"]["need_set"]

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(request_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()

        exercises_attribute = new_exercise.request_create().get("exercises_attribute")

        data_exercises_attribute = data.get("exercises_attribute")

        for attr in exercises_attribute:
            if attr == "need_set":
                self.assertEqual(data_exercises_attribute.get(attr), False)
            else:
                self.assertEqual(
                    data_exercises_attribute.get(attr), exercises_attribute.get(attr)
                )

    def test_create_exercise_with_wrong_exercises_attribute_type(self):
        """
        bool 이외의 타입으로 ExercisesAttribute 필드를 생성하려고 시도할 때 에러가 발생하는지 확인

        reverse_url : exercises-info-list
        HTTP method : POST

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. ExercisesAttribute 필드에 bool 이외의 타입으로 값을 넣은 상태로 운동 정보 생성
        4. 응답 코드가 400인지 확인
        """

        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        request_data = new_exercise.request_create()
        request_data["exercises_attribute"]["need_set"] = "test"

        response = self.client.post(
            reverse("exercises-info-list"),
            data=json.dumps(request_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_exercise_attribute(self):
        """
        ExercisesInfo 수정 시 ExercisesAttribute도 함께 수정되는지 확인

        reverse_url : exercises-info-detail
        HTTP method : PATCH

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 새 운동 정보를 생성
        3. 서버에 PATCH 요청을 보내서 ExercisesAttribute 수정
        4. 응답 코드가 200인지 확인
        5. 응답 데이터에 ExercisesAttribute의 필드 값이 모두 정의된 값과 같은지 확인
        """

        self.admin.login(self.client)

        new_exercise = FakeExercisesInfo()

        response = self.client.patch(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
            data=json.dumps(new_exercise.request_create()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        exercises_attribute = new_exercise.request_create().get("exercises_attribute")

        data_exercises_attribute = data.get("exercises_attribute")

        for attr in exercises_attribute:
            self.assertEqual(
                data_exercises_attribute.get(attr), exercises_attribute.get(attr)
            )

    def test_delete_exercise_attribute(self):
        """
        ExercisesInfo 삭제 시 ExercisesAttribute도 함께 삭제되는지 확인

        reverse_url : exercises-info-detail
        HTTP method : DELETE

        테스트 시나리오:
        1. 관리자 계정으로 로그인
        2. 생성된 운동 정보의 id로 DELETE 요청을 보냄
        3. 응답 코드가 204인지 확인
        4. ExercisesAttribute가 삭제되었는지 확인
        """

        self.admin.login(self.client)

        exercise_attribute_id = self.exercise1.instance.exercises_attribute.id

        response = self.client.delete(
            reverse("exercises-info-detail", kwargs={"pk": self.exercise1.instance.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            ExercisesAttribute.objects.filter(id=exercise_attribute_id).exists()
        )

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from account.models import CustomUser
from utils.fake_data import FakeUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginTestCase(TestCase):
    def setUp(self):
        self.user1 = FakeUser()
        self.user1.create_instance()

    def test_user_can_login(self):
        """
        테스트 로그인이 성공하는지 확인
        """
        response = self.client.post(reverse("login"), data=self.user1.request_login())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "로그인 성공")

    def test_login_by_unregisterd_user(self):
        """
        테스트 로그인이 등록되지 않은 유저일 때 실패하는지 확인
        """
        new_user = FakeUser()

        response = self.client.post(reverse("login"), data=new_user.request_login())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["message"], "로그인 실패")

    def test_login_by_wrong_password(self):
        """
        테스트 로그인이 비밀번호가 다를 때 실패하는지 확인
        """
        request_login = self.user1.request_login()
        request_login["password"] = "wrong_password"

        response = self.client.post(reverse("login"), data=request_login)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["message"], "로그인 실패")

    def test_login_by_authenticated_user(self):
        """
        로그인 된 유저가 로그인 시도 시 에러 반환
        """
        self.client.force_login(self.user1.instance)

        response = self.client.post(reverse("login"), data=self.user1.request_login())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "로그인 실패")


class SignUpTestCase(TestCase):
    def setUp(self):
        self.user1 = FakeUser()

    def test_user_can_sign_up(self):
        """
        테스트 회원가입이 성공하는지 확인
        """

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], self.user1.fake_info["username"])
        self.assertEqual(response.data["email"], self.user1.fake_info["email"])

    def test_sign_up_by_existing_username(self):
        """
        테스트 이미 존재하는 닉네임일 때 실패하는지 확인
        """
        self.user1.create_instance()

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0], "사용자의 닉네임은/는 이미 존재합니다.")

    def test_sign_up_by_existing_email(self):
        """
        테스트 이미 존재하는 이메일일 때 실패하는지 확인
        """
        self.user1.create_instance()

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "사용자의 이메일은/는 이미 존재합니다.")

    def test_sign_up_by_invalid_email(self):
        """
        테스트 이메일 형식이 잘못되었을 때 실패하는지 확인
        """
        self.user1.fake_info["email"] = "invalid_email"

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "유효한 이메일 주소를 입력하십시오.")

    def test_sign_up_by_invalid_password(self):
        """
        테스트 비밀번호가 너무 짧을 때 실패하는지 확인
        """
        self.user1.fake_info["password"] = "short"

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["password"][0],
            "이 필드의 글자 수가  적어도 8 이상인지 확인하십시오.",
        )

    def test_sign_up_by_long_password(self):
        """
        테스트 비밀번호가 너무 길 때 실패하는지 확인
        """
        self.user1.fake_info["password"] = "a" * 21

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["password"][0],
            "이 필드의 글자 수가 20 이하인지 확인하십시오.",
        )

    def test_sign_up_by_invalid_username(self):
        """
        테스트 닉네임이 너무 길 때 실패하는지 확인
        """
        self.user1.fake_info["username"] = "a" * 21

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["username"][0],
            "이 필드의 글자 수가 20 이하인지 확인하십시오.",
        )

    def test_sign_up_by_blank_username(self):
        """
        테스트 닉네임이 공백일 때 실패하는지 확인
        """
        self.user1.fake_info["username"] = ""

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0], "이 필드는 blank일 수 없습니다.")

    def test_sign_up_by_blank_email(self):
        """
        테스트 이메일이 공백일 때 실패하는지 확인
        """
        self.user1.fake_info["email"] = ""

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "이 필드는 blank일 수 없습니다.")

    def test_sign_up_by_long_email(self):
        """
        테스트 이메일 길이 제한을 넘었을 때 실패하는지 확인
        """
        self.user1.fake_info["email"] = "a" * 50 + "@test.com"

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "이 필드의 글자 수가 50 이하인지 확인하십시오.")

    def test_sign_up_by_invalid_username(self):
        """
        테스트 닉네임 형식이 잘못되었을 때 실패하는지 확인
        """
        self.user1.fake_info["username"] = "invalid username"

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["username"][0],
            "이 필드에는 영문자, 숫자, 밑줄만 포함할 수 있습니다.",
        )

    def test_sign_up_by_invalid_password(self):
        """
        테스트 패스워드 형식이 잘못되었을 때 실패하는지 확인
        """
        self.user1.fake_info["password"] = "password"

        response = self.client.post(reverse("signup"), data=self.user1.request_create())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["password"][0],
            "비밀번호는 숫자, 문자, 특수문자를 모두 포함해야 합니다.",
        )


class LogoutTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword1!"
        )

    def test_user_can_logout(self):
        # 로그인을 시도하여 토큰을 발급받습니다.
        login_url = reverse("token_obtain_pair")
        login_data = {"email": "test@example.com", "password": "testpassword"}
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 발급받은 토큰을 헤더에 포함하여 로그아웃을 요청합니다.
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)
        logout_url = reverse("logout")
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "로그아웃 성공")

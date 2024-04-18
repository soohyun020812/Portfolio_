from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from account.models import CustomUser as User
from utils.fake_data import FakePost, FakeUser

from .models import Post
from .serializers import PostSerializer


class PostTestCase(TestCase):
    def setUp(self):
        self.user1 = FakeUser()
        self.user1.create_instance()

        self.user2 = FakeUser()
        self.user2.create_instance()

        self.user1_post1 = FakePost()
        self.user1_post1.create_instance(user_instance=self.user1.instance)

        self.user1_post2 = FakePost()
        self.user1_post2.create_instance(user_instance=self.user1.instance)

        self.user2_post1 = FakePost()
        self.user2_post1.create_instance(user_instance=self.user2.instance)

    def test_get_post_list(self):
        """post/ GET 요청시 모든 Post 객체를 반환하는지 테스트"""
        post_count = Post.objects.all().count()

        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), post_count)

    def test_get_post_detail(self):
        """post/<pk>/ GET 요청시 해당 Post 객체를 반환하는지 테스트"""
        response = self.client.get(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.user1_post1.instance.title)
        self.assertEqual(response.data["content"], self.user1_post1.instance.content)

    def test_create_post(self):
        """post/ POST 요청시 새로운 Post 객체를 생성하는지 테스트"""
        new_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.post(reverse("post-list"), new_post.request_create())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["title"], new_post.request_create()["title"])
        self.assertEqual(data["content"], new_post.request_create()["content"])

    def test_create_post_without_login(self):
        """post/ POST 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        new_post = FakePost()

        response = self.client.post(reverse("post-list"), new_post.request_create())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_post(self):
        """post/<pk>/ PATCH 요청시 해당 Post 객체를 수정하는지 테스트"""
        update_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id}),
            data=update_post.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], update_post.request_create()["title"])
        self.assertEqual(data["content"], update_post.request_create()["content"])

    def test_update_post_without_login(self):
        """post/<pk>/ PATCH 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        update_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id}),
            data=update_post.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        """post/<pk>/ DELETE 요청시 해당 Post 객체를 삭제하는지 테스트"""
        self.client.force_login(self.user1.instance)

        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.user1_post1.instance.id).exists())

    def test_delete_post_without_login(self):
        """post/<pk>/ DELETE 요청시 로그인하지 않은 경우 403 에러를 반환하는지 테스트"""
        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_update_post_not_allowed(self):
        """post/<pk>/ PUT 요청시 405 에러를 반환하는지 테스트"""
        update_post = FakePost()

        self.client.force_login(self.user1.instance)

        response = self.client.put(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id}),
            data=update_post.request_create(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # TODO: 다른사람도 포스트를 볼 수 있어야 합니다
    def test_get_only_logged_in_user_posts(self):
        """post/ GET 요청시 로그인한 사용자의 Post 객체만 반환하는지 테스트"""
        self.client.force_login(self.user1.instance)
        response = self.client.get(reverse("post-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 숫자 대신 원하는 값을 직접 쿼리로 가져와서 비교하는게 좋습니다.

    # TODO: 다른사람도 포스트를 볼 수 있어야 합니다
    def test_get_only_logged_in_user_post_detail(self):
        """post/<pk>/ GET 요청시 로그인한 사용자의 특정 Post 객체만 반환하는지 테스트"""
        self.client.force_login(self.user1.instance)
        response = self.client.get(
            reverse("post-detail", kwargs={"pk": self.user1_post1.instance.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.user1_post1.instance.title)
        self.assertEqual(response.data["content"], self.user1_post1.instance.content)

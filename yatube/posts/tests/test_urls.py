from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="HasNoName")
        cls.user_2 = User.objects.create_user(username="HasNoName2")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )

        cls.post = Post.objects.create(
            text="Пост HasNoName",
            group=cls.group,
            author=cls.user,
        )

        cls.post_2 = Post.objects.create(
            text="Пост HasNoName2",
            group=cls.group,
            author=cls.user_2,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_url_exists_at_desired_location_guest_client(self):
        posts_urls = {
            "/": HTTPStatus.OK,
            f"/group/{PostsURLTests.group.slug}/": HTTPStatus.OK,
            f"/profile/{PostsURLTests.user.username}/": HTTPStatus.OK,
            f"/posts/{PostsURLTests.post.pk}/": HTTPStatus.OK,
            "/unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for page, expected_value in posts_urls.items():
            response = self.client.get(page)
            with self.subTest(page=page):
                self.assertEqual(response.status_code, expected_value)

    def test_url_exists_at_desired_location_authorized_client(self):
        posts_urls = {
            "/": HTTPStatus.OK,
            f"/group/{PostsURLTests.group.slug}/": HTTPStatus.OK,
            f"/profile/{PostsURLTests.user.username}/": HTTPStatus.OK,
            f"/posts/{PostsURLTests.post.pk}/": HTTPStatus.OK,
            f"/posts/{PostsURLTests.post.pk}/edit/": HTTPStatus.OK,
            "/create/": HTTPStatus.OK,
            "/unexisting_page/": HTTPStatus.NOT_FOUND,
        }
        for page, expected_value in posts_urls.items():
            response = self.authorized_client.get(page)
            with self.subTest(page=page):
                self.assertEqual(response.status_code, expected_value)

    def test_url_uses_correct_template(self):
        posts_urls = {
            "/": "posts/index.html",
            f"/group/{PostsURLTests.group.slug}/": "posts/group_list.html",
            f"/profile/{PostsURLTests.user.username}/": "posts/profile.html",
            f"/posts/{PostsURLTests.post.pk}/": "posts/post_detail.html",
            f"/posts/{PostsURLTests.post.pk}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
            "/unexisting_page/": "core/404.html",
        }
        for page, expected_value in posts_urls.items():
            response = self.authorized_client.get(page)
            with self.subTest(page=page):
                self.assertTemplateUsed(response, expected_value)

    def test_url_redirect_guest_client(self):
        posts_urls = {
            f"/posts/{PostsURLTests.post.pk}/edit/": (
                f"/auth/login/?next=/posts/{PostsURLTests.post.pk}/edit/"
            ),
            "/create/": "/auth/login/?next=/create/",
        }
        for page, expected_value in posts_urls.items():
            response = self.client.get(page, follow=True)
            with self.subTest(page=page):
                self.assertRedirects(response, expected_value)

    def test_url_redirect_authorized_client(self):
        response = self.authorized_client.get(
            f"/posts/{PostsURLTests.post_2.pk}/edit/", follow=True
        )
        self.assertRedirects(response, f"/posts/{PostsURLTests.post_2.pk}/")

    def test_cache_index_page(self):
        response = self.client.get(reverse("posts:index"))
        Post.objects.filter(pk=self.post_2.pk).get().delete()
        response_2 = self.client.get(reverse("posts:index"))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.client.get(reverse("posts:index"))
        self.assertNotEqual(response.content, response_3.content)

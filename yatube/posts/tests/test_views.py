import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.group_2 = Group.objects.create(
            title="Тестовая группа_2",
            slug="test-slug_2",
            description="Тестовое описание_2",
        )
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Пост HasNoName",
            group=cls.group,
            author=cls.user,
        )
        cls.post_2 = Post.objects.create(
            text="Пост HasNoName_2",
            group=cls.group_2,
            author=cls.user_2,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def compare_context(self, url, client_type, page_context):
        response = client_type.get(url)
        if page_context != "page_obj":
            response_context = response.context[page_context]
        else:
            response_context = response.context[page_context][0]
        if url != (reverse("posts:post_create")) and url != (
            reverse(
                "posts:post_edit",
                kwargs={"post_id": PostsURLTests.post.pk},
            )
        ):
            self.assertEqual(
                response_context.text,
                PostsURLTests.post_2.text,
            )
            self.assertEqual(
                response_context.author,
                PostsURLTests.post_2.author,
            )
            self.assertEqual(
                response_context.group,
                PostsURLTests.post_2.group,
            )
            self.assertEqual(
                response_context.image,
                PostsURLTests.post_2.image,
            )
            if url == reverse("posts:index"):
                self.assertEqual(
                    response_context.pub_date,
                    PostsURLTests.post_2.pub_date,
                )
            if url != reverse(
                "posts:post_detail",
                kwargs={"post_id": PostsURLTests.post_2.pk},
            ):
                self.assertEqual(
                    response_context.pk,
                    PostsURLTests.post_2.pk,
                )
        else:
            expected = forms.fields.CharField
            form_field = response.context.get(page_context).fields.get("text")
            self.assertIsInstance(form_field, expected)

    def test_pages_uses_correct_template(self):
        posts_urls = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group", kwargs={"slug": PostsURLTests.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile",
                kwargs={"username": PostsURLTests.user.username},
            ): "posts/profile.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostsURLTests.post.pk},
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": PostsURLTests.post.pk},
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in posts_urls.items():
            response = self.authorized_client.get(reverse_name)
            with self.subTest(template=template):
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        url = reverse("posts:index")
        client_type = self.client
        page_context = "page_obj"
        PostsURLTests.compare_context(self, url, client_type, page_context)

    def test_group_list_show_correct_context(self):
        url = reverse(
            "posts:group", kwargs={"slug": PostsURLTests.group_2.slug}
        )
        client_type = self.client
        page_context = "page_obj"
        PostsURLTests.compare_context(self, url, client_type, page_context)

    def test_profile_show_correct_context(self):
        url = reverse(
            "posts:profile",
            kwargs={"username": PostsURLTests.user_2.username},
        )
        client_type = self.client
        page_context = "page_obj"
        PostsURLTests.compare_context(self, url, client_type, page_context)

    def test_post_detail_show_correct_context(self):
        url = reverse(
            "posts:post_detail",
            kwargs={"post_id": PostsURLTests.post_2.pk},
        )
        client_type = self.client
        page_context = "post"
        PostsURLTests.compare_context(self, url, client_type, page_context)

    def test_post_create_show_correct_context(self):
        url = reverse("posts:post_create")
        client_type = self.authorized_client
        page_context = "form"
        PostsURLTests.compare_context(self, url, client_type, page_context)

    def test_post_edit_show_correct_context(self):
        url = reverse(
            "posts:post_edit",
            kwargs={"post_id": PostsURLTests.post.pk},
        )
        client_type = self.authorized_client
        page_context = "form"
        PostsURLTests.compare_context(self, url, client_type, page_context)

    def test_post_with_group(self):
        response = self.client.get(reverse("posts:index"))
        response_result = response.context["page_obj"][0].group
        self.assertEqual(response_result, PostsURLTests.group_2)
        response = self.client.get(
            reverse("posts:group", kwargs={"slug": PostsURLTests.group.slug})
        )
        self.assertEqual(response_result, PostsURLTests.group_2)
        response = self.client.get(
            reverse(
                "posts:profile",
                kwargs={"username": PostsURLTests.user_2.username},
            )
        )
        self.assertEqual(response_result, PostsURLTests.group_2)
        response = self.client.get(
            reverse("posts:group", kwargs={"slug": PostsURLTests.group.slug})
        )
        self.assertNotEqual(response_result, PostsURLTests.group)

    def test_create_follow_authorized_client(self):
        self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": PostsURLTests.user_2.username},
            )
        )
        follow = Follow.objects.latest("pk")
        self.assertEqual(follow.user, PostsURLTests.user)
        self.assertEqual(follow.author, PostsURLTests.user_2)

    def test_delete_follow_authorized_client(self):
        self.authorized_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": PostsURLTests.user_2.username},
            )
        )
        follow = Follow.objects.filter(
            user=PostsURLTests.user, author=PostsURLTests.user_2
        ).first()
        self.assertIsNone(follow)

    def test_new_post_in_follower_authorized_client(self):
        self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": PostsURLTests.user_2.username},
            )
        )
        new_post = Post.objects.create(
            text="New post",
            group=PostsURLTests.group_2,
            author=PostsURLTests.user_2,
        )
        response = self.authorized_client.get(reverse("posts:follow_index"))
        response_result = response.context["page_obj"][0]
        self.assertEqual(response_result, new_post)

    def test_new_post_not_in_not_follower_authorized_client(self):
        self.authorized_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": PostsURLTests.user_2.username},
            )
        )
        new_post = Post.objects.create(
            text="New post",
            group=PostsURLTests.group,
            author=PostsURLTests.user,
        )
        response = self.authorized_client.get(reverse("posts:follow_index"))
        response_result = response.context["page_obj"][0]
        self.assertNotEqual(response_result, new_post)


class PaginatorTests(TestCase):
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
        cls.group_2 = Group.objects.create(
            title="Тестовая группа_2",
            slug="test-slug_2",
            description="Тестовое описание_2",
        )
        cls.posts_obj = []
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    author=cls.user,
                    text=f"Пост_{i} HasNoName",
                    group=cls.group,
                )
                for i in range(11)
            ]
        )
        cls.posts = Post.objects.bulk_create(cls.posts_obj)
        cls.post_12 = Post.objects.create(
            text="Пост_12 HasNoName",
            group=cls.group_2,
            author=cls.user,
        )

        cls.post_13 = Post.objects.create(
            text="Пост_13 HasNoName_2",
            group=cls.group_2,
            author=cls.user_2,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTests.user)

    def test_first_page_contains_ten_records(self):
        paginator_urls = [
            reverse("posts:index"),
            reverse("posts:group", kwargs={"slug": PaginatorTests.group.slug}),
            reverse(
                "posts:profile",
                kwargs={"username": PaginatorTests.user.username},
            ),
        ]
        for url in paginator_urls:
            response = self.authorized_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(
                    len(response.context["page_obj"]), settings.POSTS_QUANTITY
                )

    def test_second_page_contains_three_records(self):
        remain_posts = Post.objects.count() - settings.POSTS_QUANTITY
        if remain_posts >= settings.POSTS_QUANTITY:
            all_posts_count_second_page = settings.POSTS_QUANTITY
        else:
            all_posts_count_second_page = remain_posts
        remain_posts_group = (
            Post.objects.filter(group=PaginatorTests.group).count()
            - settings.POSTS_QUANTITY
        )
        if remain_posts_group >= settings.POSTS_QUANTITY:
            group_posts_count_second_page = settings.POSTS_QUANTITY
        else:
            group_posts_count_second_page = remain_posts_group
        remain_posts_user = (
            Post.objects.filter(author=PaginatorTests.user).count()
            - settings.POSTS_QUANTITY
        )
        if remain_posts_user >= settings.POSTS_QUANTITY:
            user_posts_count_second_page = settings.POSTS_QUANTITY
        else:
            user_posts_count_second_page = remain_posts_user
        paginator_urls = {
            reverse("posts:index"): all_posts_count_second_page,
            reverse(
                "posts:group", kwargs={"slug": PaginatorTests.group.slug}
            ): group_posts_count_second_page,
            reverse(
                "posts:profile",
                kwargs={"username": PaginatorTests.user.username},
            ): user_posts_count_second_page,
        }

        for url, posts_second_page in paginator_urls.items():
            response = self.authorized_client.get(url + "?page=2")
            with self.subTest(url=url):
                self.assertEqual(
                    len(response.context["page_obj"]), posts_second_page
                )

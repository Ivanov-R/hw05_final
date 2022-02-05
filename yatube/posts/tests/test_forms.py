import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="HasNoName")
        cls.user_2 = User.objects.create_user(username="HasNoName_2")
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
        cls.post = Post.objects.create(
            text="Пост HasNoName",
            group=cls.group,
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text="Тестовый комментарий",
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFormsTests.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(PostsFormsTests.user_2)

    def test_form_created_new_post(self):
        posts_count = Post.objects.count()
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
        form_data = {
            "text": "New Post",
            "group": PostsFormsTests.group.pk,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        latest_post = Post.objects.latest("pk")
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={"username": PostsFormsTests.user.username},
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(latest_post.text, form_data["text"])
        self.assertEqual(latest_post.group.pk, form_data["group"])

    def test_form_post_edit(self):
        post_id = PostsFormsTests.post.pk
        small_2_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x00"
        )
        uploaded_2 = SimpleUploadedFile(
            name="small_2.gif", content=small_2_gif, content_type="image/gif"
        )
        form_data_edited = {
            "text": "Edited Post",
            "group": PostsFormsTests.group_2.pk,
            "image": uploaded_2,
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": post_id}),
            data=form_data_edited,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": post_id},
            ),
        )
        post_edited = Post.objects.get(pk=post_id)
        self.assertEqual(
            post_edited.text,
            form_data_edited["text"],
        )
        self.assertEqual(
            post_edited.group.pk,
            form_data_edited["group"],
        )

    def test_form_new_post_cannot_be_created_by_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "New Post by guest",
            "group": PostsFormsTests.group.pk,
        }
        response = self.client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next=/create/',
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_form_post_cannot_be_edited_by_guest(self):
        post_id = PostsFormsTests.post.pk
        redirect_url = reverse("posts:post_edit", kwargs={"post_id": post_id})
        form_data_edited_by_guest = {
            "text": "Edited by guest post",
            "group": PostsFormsTests.group_2.pk,
        }
        response = self.client.post(
            reverse("posts:post_edit", kwargs={"post_id": post_id}),
            data=form_data_edited_by_guest,
            follow=True,
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={redirect_url}',
        ),
        post_edited = Post.objects.get(pk=post_id)
        self.assertNotEqual(
            post_edited.text,
            form_data_edited_by_guest["text"],
        )
        self.assertNotEqual(
            post_edited.group.pk,
            form_data_edited_by_guest["group"],
        )

    def test_form_post_cannot_be_edited_by_not_author(self):
        post_id = PostsFormsTests.post.pk
        form_data_edited_by_not_author = {
            "text": "Edited by not author",
            "group": PostsFormsTests.group_2.pk,
        }
        response = self.authorized_client_2.post(
            reverse("posts:post_edit", kwargs={"post_id": post_id}),
            data=form_data_edited_by_not_author,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": post_id},
            ),
        ),
        post_edited = Post.objects.get(pk=post_id)
        self.assertNotEqual(
            post_edited.text,
            form_data_edited_by_not_author["text"],
        )
        self.assertNotEqual(
            post_edited.group.pk,
            form_data_edited_by_not_author["group"],
        )

    def test_form_new_comment_cannot_be_created_by_guest(self):
        comments_count = Comment.objects.count()
        post_id = PostsFormsTests.post.pk
        redirect_url = reverse(
            "posts:add_comment", kwargs={"post_id": post_id}
        )
        form_data = {
            "text": "New Comment by guest",
        }
        response = self.client.post(
            reverse(
                "posts:add_comment",
                kwargs={"post_id": post_id},
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={redirect_url}',
        )
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_form_created_new_comment(self):
        comments_count = Comment.objects.count()
        post_id = PostsFormsTests.post.pk
        form_data = {
            "text": "New Comment",
        }
        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": post_id}),
            data=form_data,
            follow=True,
        )
        latest_comment = Comment.objects.latest("pk")
        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": post_id},
            ),
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(latest_comment.text, form_data["text"])
        self.assertEqual(latest_comment.post.pk, PostsFormsTests.post.pk)

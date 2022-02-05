from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовая группа",
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text="Тестовый комментарий",
            post=cls.post,
        )

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        str_group = group.title
        self.assertEqual(
            str_group, str(group), "__str__ группы работает некорректно"
        )
        post = PostModelTest.post
        str_post = post.text[:15]
        self.assertEqual(
            str_post, str(post), "__str__ поста работает некорректно"
        )
        comment = PostModelTest.comment
        str_post = comment.text[:15]
        self.assertEqual(
            str_post, str(comment), "__str__ поста работает некорректно"
        )

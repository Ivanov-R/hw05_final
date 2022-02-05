from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        static_pages = {
            "/about/author/": 200,
            "/about/tech/": 200,
        }
        for static_page, expected_value in static_pages.items():
            response = self.guest_client.get(static_page)
            with self.subTest(static_page=static_page):
                self.assertEqual(response.status_code, expected_value)

    def test_about_url_uses_correct_template(self):
        static_pages = {
            "/about/author/": "about/author.html",
            "/about/tech/": "about/tech.html",
        }
        for static_page, expected_value in static_pages.items():
            response = self.guest_client.get(static_page)
            with self.subTest(static_page=static_page):
                self.assertTemplateUsed(response, expected_value)

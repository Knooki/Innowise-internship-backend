from django.test import TestCase

from posts.models import Page
from accounts.models import User


class PageModelTestCase(TestCase):
    def setUp(self):
        self.page = Page(
            name="test_page",
            uuid="test",
            description="test",
            owner=User(username="test", password="test", email="test@gmail.com"),
        )

    def test_page_returns_str(self):
        self.assertEqual(str(self.page), "test_page")

from django.test import TestCase

from .models import Tag, Page, Post


class TagTestCase(TestCase):
    fixtures = ['fixtures.json']

    def test_tag_returns_str(self):
        test_tag = Tag.objects.get(pk=1)
        self.assertEqual(str(test_tag), "test_tag")


class PageTestCase(TestCase):
    fixtures = ['fixtures.json']

    def test_page_returns_str(self):
        test_page = Page.objects.get(pk=1)
        self.assertEqual(str(test_page), "test_page")


class PostTestCase(TestCase):
    fixtures = ['fixtures.json']

    def test_post_returns_str(self):
        test_post = Post.objects.get(pk=1)
        self.assertEqual(str(test_post), "test_post")

from django.test import TestCase, Client
from django.urls import reverse


class TestFrontPageUI(TestCase):

    def test_front_page_loads(self):
        c = Client()
        target = reverse('ui/front_page')
        result = c.get(target)
        self.assertEqual(result.status_code, 200)

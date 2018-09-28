from django.test import Client, TestCase

from main.tests.factories.user_factory import UserFactory


class UITestCase(TestCase):

    def three_perm_check(self, target, authorized_user, not_logged_in, logged_in, authorised):
        """

        :param target: target url to request
        :param authorized_user: user that has permissions to access page
        :param not_logged_in: status code expected by not logged in user
        :param logged_in: status code expected by logged in user
        :param authorised: status code expected by an authorised user
        """
        c = Client()
        response = c.get(target)
        self.assertEqual(response.status_code, not_logged_in)
        c.force_login(UserFactory())
        response = c.get(target)
        self.assertEqual(response.status_code, logged_in)
        c.force_login(authorized_user)
        response = c.get(target)
        self.assertEqual(response.status_code, authorised)

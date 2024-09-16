"""Tests of user authentication.

Put this file in a subdirectory of your ku-polls project,
for example, a directory named "auth".
Then run: manage.py test auth

"""

import django.test
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate  # to "login" a user using code
from polls.models import Question, Choice
from mysite import settings


class UserAuthTest(django.test.TestCase):
    """Test user authentication."""

    def setUp(self):
        """Set up the test."""
        # superclass setUp creates a Client object
        # and initializes test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q
        self.vote_url = reverse("polls:vote", args=[self.question.id])

    def test_logout(self):
        """A user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        # Authenticate the user.
        # We want to logout this user, so we need to associate the
        # user user with a session.  Setting client.user = ... doesn't work.
        # Use Client.login(username, password) to do that.
        # Client.login returns true on success
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # visit the logout page
        form_data = {}
        response = self.client.post(logout_url, form_data)
        self.assertEqual(302, response.status_code)

        # should redirect us to where? Polls index? Login?
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": self.username, "password": self.password}
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
          or I receive a 403 response (FORBIDDEN)
        """
        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(self.vote_url, form_data)
        # should be redirected to the login page
        self.assertEqual(response.status_code, 302)  # could be 303
        # this test fails because reverse('login') does not include
        # the query parameter ?next=/polls/1/vote/
        # self.assertRedirects(response, reverse('login') )
        # How to fix it?
        login_with_next = f"{reverse('login')}?next={self.vote_url}"
        self.assertRedirects(response, login_with_next)

    def test_wrong_password(self):
        """Test when user submits a wrong password."""
        wrong_password = self.password + "junk"
        user = authenticate(username=self.username, password=wrong_password)
        self.assertIsNone(user)

    def test_invalid_user(self):
        """Test when invalid user is trying to log in."""
        invalid_username = self.username + "skibidi_toilet"
        user = authenticate(username=invalid_username, password=self.password)
        self.assertIsNone(user)

    def test_user_can_vote(self):
        """Test that authorized users can successfully vote in a poll."""
        choice = self.question.choice_set.first()
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )

        form_data = {"choice": f"{choice.id}"}
        self.client.post(self.vote_url, form_data)
        vote_object = choice.vote_set.get(user=self.user1)
        self.assertEqual(vote_object.user, self.user1)

    def test_user_can_change_vote(self):
        """Test that the user can successfully change vote."""
        choice_before = self.question.choice_set.first()
        choice_after = self.question.choice_set.get(choice_text__contains="2")
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )

        form_data_before = {"choice": f"{choice_before.id}"}
        form_data_after = {"choice": f"{choice_after.id}"}
        self.client.post(self.vote_url, form_data_before)
        self.client.post(self.vote_url, form_data_after)
        vote_object = choice_after.vote_set.get(user=self.user1)
        self.assertEqual(choice_before.votes, 0)
        self.assertEqual(choice_after.votes, 1)
        self.assertEqual(vote_object.user, self.user1)

    def test_one_vote_per_user(self):
        """Test that one user can vote only once on a question."""
        choice = self.question.choice_set.first()
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )

        form_data = {"choice": f"{choice.id}"}
        for _ in range(5):
            self.client.post(self.vote_url, form_data)
        vote_object = choice.vote_set.get(user=self.user1)
        self.assertEqual(vote_object.user, self.user1)
        self.assertEqual(choice.votes, 1)

    def test_user_can_delete_vote(self):
        """Test that authenticated user can delete his vote."""
        choice = self.question.choice_set.first()
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )

        form_data = {"choice": f"{choice.id}"}
        self.client.post(self.vote_url, form_data)
        form_data = {"choice": f"{choice.id}"}
        self.client.post(self.vote_url, form_data)
        unvote_url = reverse("polls:unvote", args=[self.question.id])
        self.client.post(unvote_url)
        self.assertEqual(choice.vote_set.filter(user=self.user1).count(), 0)

"""Test that views display elements properly."""
import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from polls.models import Question


def create_question(question_text, days):
    """
    Create a question, without end date, with the given `question_text`.

    And published the given number of `days` offset to now
    (negative for questions published in the past,
    positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(
        question_text=question_text, pub_date=time, end_date=None
    )


def create_question_2(t1, t2):
    """
    Create a question with publication date AND END DATE.

    Args:
        t1 (_type_): publication date offset
        t2 (_type_): end date offset

    Returns:
        the question
    """
    pub_date = timezone.now() + datetime.timedelta(seconds=t1)
    end_date = timezone.now() + datetime.timedelta(seconds=t2)
    question = Question.objects.create(
        question_text="Placeholder", pub_date=pub_date, end_date=end_date
    )
    return question


class QuestionIndexViewTests(TestCase):
    """Test the index view."""

    def test_no_questions(self):
        """If no questions exist, an appropriate message is displayed."""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """Published questions are displayed on the index page."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """Unpublished questions aren't displayed on the index page."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Only past questions should be displayed.

        In the case that there're both past and future questions.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """The questions index page may display multiple questions."""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    """Test the detail view."""

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future.

        Redirects to the index page.
        """
        future_question = create_question(question_text="Future Question",
                                          days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse("polls:index"))

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past.

        Displays the question's text.
        """
        past_question = create_question(question_text="Past Question.",
                                        days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

"""Test that the methods of the models are working properly."""
import datetime

from django.test import TestCase
from django.utils import timezone

from polls.models import Question


def create_question(question_text, days):
    """
    Create a question, with the given `question_text` with publication date offset.

    (negative for questions published in the past,
    positive for questions that have yet to be published.
    Questions created with this method have no end date.).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(
        question_text=question_text, pub_date=time, end_date=None
    )


def create_question_2(t1, t2):
    """
    Create a question with publication date AND END DATE.

    Args:
        t1: publication date offset
        t2: end date offset

    Returns:
        the question
    """
    pub_date = timezone.now() + datetime.timedelta(seconds=t1)
    end_date = timezone.now() + datetime.timedelta(seconds=t2)
    question = Question.objects.create(
        question_text="Placeholder", pub_date=pub_date, end_date=end_date
    )
    return question


class WasPublishedRecentlyTests(TestCase):
    """Test whether was_published_recently method is working properly."""

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() returns False for questions whose pub_date is in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """was_published_recently() returns False for questions that are older than 1 day."""
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """was_published_recently() returns True for questions that aren't older than 1 day."""
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class IsPublishedTests(TestCase):
    """Test whether is_published method is working properly."""

    def test_question_with_future_pub_date(self):
        """Test questions with publication date in the future."""
        question = create_question("Future Question", 30)
        self.assertIs(question.is_published(), False)

    def test_question_with_default_pub_date(self):
        """Test questions with publication date in the future."""
        question = Question.objects.create(question_text="Present Question")
        self.assertIs(question.is_published(), True)

    def test_question_with_past_pub_date(self):
        """Test questions with publication date in the future."""
        question = create_question("Past Question", -30)
        self.assertIs(question.is_published(), True)


class CanVoteTests(TestCase):
    """Test whether can_vote method is working properly."""

    def test_cannot_vote_after_end_date(self):
        """Test voting on a question that's already past its end date."""
        question = create_question_2(-30, -1)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_during_valid_time(self):
        """Test voting on a legal question."""
        question = create_question_2(-30, 30)
        self.assertIs(question.can_vote(), True)

    def test_cannot_vote_future_question(self):
        """Test voting on a question that hasn't been published yet."""
        question = create_question_2(1, 30)
        self.assertIs(question.can_vote(), False)

    def test_can_vote_on_question_with_no_end_date(self):
        """Test voting on a question with no end date."""
        question = create_question("Placeholder", -30)
        question2 = Question.objects.create(question_text="Present Question")
        self.assertIs(question.can_vote(), True)
        self.assertIs(question2.can_vote(), True)

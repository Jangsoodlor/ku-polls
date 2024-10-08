"""Contains models for the poll application."""

import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """
    The Question model.

    Contains two fields, which are the question text and the publication date.
    """

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", default=timezone.now)
    end_date = models.DateTimeField(
        "ending date for voting", default=None, null=True, blank=True
    )

    def __str__(self):
        """Retrieve the question's text."""
        return self.question_text

    def was_published_recently(self):
        """Check whether the poll was published recently."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """Check whether the poll is published."""
        return self.pub_date <= timezone.now()

    def can_vote(self):
        """Check whether the user can vote on the poll."""
        if self.end_date:
            return self.is_published() and timezone.now() <= self.end_date
        return self.is_published()


class Choice(models.Model):
    """
    The choice Model.

    There can be many choices to one question.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self):
        """Return the vote of this choice."""
        return self.vote_set.count()

    def __str__(self):
        """Return the choice's text."""
        return self.choice_text


class Vote(models.Model):
    """
    A vote by the user to a choice in the poll.

    There can be many votes to one choice.
    """

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

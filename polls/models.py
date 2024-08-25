"""Contains models for the poll application"""
import datetime
from django.db import models
from django.utils import timezone

class Question(models.Model):
    """
    The Question model. Contains two fields, which are the question text
    and the publication date.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        """Returns the question's text"""
        return self.question_text

    def was_published_recently(self):
        """Check whether the poll was published recently"""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now



class Choice(models.Model):
    """
    The choice Model. It has Question as a Foreign Key, meaning that there can
    be many choice to one question. Also contain the choice_text and votes fields
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Returns the choice's text"""
        return self.choice_text

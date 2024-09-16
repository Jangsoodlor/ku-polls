"""Contains the views of the poll application."""

import logging
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib import messages
from django.contrib.auth import user_logged_in, \
                                user_login_failed, \
                                user_logged_out
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from .models import Choice, Question, Vote

logger = logging.getLogger("polls")


class IndexView(generic.ListView):
    """The view of the poll's index page."""

    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        questions = Question.objects.filter(pub_date__lte=timezone.now())
        return questions.order_by("-pub_date")


class DetailView(generic.DetailView):
    """Display choices for a poll."""

    model = Question
    template_name = "polls/detail.html"

    def dispatch(self, request, *args, **kwargs):
        """Check whether the question can be voted on.

        If not, then redirects to the index page with error message.
        """
        question = self.get_object()
        if not question.can_vote():
            error_text = "Access Denied."
            messages.error(request, error_text)
            return HttpResponseRedirect(reverse("polls:index"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add user's selected choice to the context, if exists."""
        data = super().get_context_data(**kwargs)
        question = self.get_object()
        user = self.request.user
        if user.is_authenticated:
            marked_vote = user.vote_set.filter(choice__question=question)
            if marked_vote:
                data["marked_choice"] = marked_vote.first().choice
        return data


class ResultsView(generic.DetailView):
    """The view of the results page."""

    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """If the user is eligible to vote, cast a vote to the active question."""
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        logger.error(
            f"Failed to get selected choice for question {question_id}"
        )
        messages.error(request, "Please re-select the choice again.")
        return HttpResponseRedirect(reverse("polls:detail",
                                            args=(question.id,)))

    this_user = request.user
    try:
        vote = this_user.vote_set.get(choice__question=question,
                                      user=this_user)
        vote.choice = selected_choice
        vote.save()
        vote_id = selected_choice.id
        logger.info(
            f"{this_user} changed vote to vote id: {vote_id} \
on question id: {question.id}"
        )
        messages.success(request, f'Your vote was changed to \
"{selected_choice.choice_text}"')
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        logger.info(
            f"{this_user} voted vote id: {selected_choice.id} \
on question id: {question.id}"
        )
        messages.success(request, f'You have voted \
"{selected_choice.choice_text}"')

    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


@login_required
def unvote(request, question_id):
    """Delete the user's vote, if exists."""
    question = get_object_or_404(Question, pk=question_id)
    this_user = request.user

    try:
        vote = this_user.vote_set.get(choice__question=question,
                                      user=this_user)
        logger.info(f"{this_user} deleted vote id: {vote.id} \
on question id: {question.id}")
        vote.delete()
        messages.success(request, "You've successfully deleted your vote")
    except Vote.DoesNotExist:
        messages.error(request, "ERROR: You haven't vote yet")
        logger.error(
            f"{this_user} tried to delete non-existent vote \
on question id: {question.id}"
        )
        return HttpResponseRedirect(reverse("polls:detail",
                                            args=(question.id,)))

    return HttpResponseRedirect(reverse("polls:results",
                                        args=(question.id,)))


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
    return None


@receiver(user_logged_in)
def login_success(sender, request, user, **kwargs):
    """Log when user successfully login."""
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged in from {ip_addr}")


@receiver(user_logged_out)
def logout_success(sender, request, user, **kwargs):
    """Log when user successfully log out."""
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged out from {ip_addr}")


@receiver(user_login_failed)
def login_fail(sender, credentials, request, **kwargs):
    """Log when user failed to login."""
    ip_addr = get_client_ip(request)
    logger.warning(f"Failed login for {credentials['username']} \
from {ip_addr}")

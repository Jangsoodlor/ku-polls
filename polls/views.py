from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    """The view of the poll's index page"""

    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """Display choices for a poll"""

    model = Question
    template_name = "polls/detail.html"

    def dispatch(self, request, *args, **kwargs):
        question = self.get_object()
        if not question.can_vote():
            messages.error(request, "ERROR: You don't have access to that poll!")
            return HttpResponseRedirect(reverse("polls:index"))
        return super().dispatch(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    """The view of the results page"""

    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """The code for the voting process"""

    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        context = {
            "question": question,
            "error_message": "You didn't select a choice.",
        }
        return render(request, "polls/detail.html", context)

    this_user = request.user
    try:
        vote = this_user.vote_set.get(choice__question=question, user=this_user)
        vote.choice=selected_choice
        vote.save()
        messages.success(request, f'Your vote was changed to "{selected_choice.choice_text}"')
    except Vote.DoesNotExist:
        vote = Vote.objects.create(user=this_user, choice=selected_choice)
        messages.success(request, "Your choice has been successfully recorded. Thank you.")

    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

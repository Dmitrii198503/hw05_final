from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUp(CreateView):
    """Creates Sign up view"""
    form_class = CreationForm
    sucess_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'

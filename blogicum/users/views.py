from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView


class RegistrationView(CreateView):
    """Представление для регистрации нового пользователя."""

    form_class = UserCreationForm
    template_name = 'auth/registration.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        """Автоматически авторизуем пользователя после регистрации."""
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

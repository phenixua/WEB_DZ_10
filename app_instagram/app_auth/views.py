from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from .forms import RegisterForm


# Create your views here.

class RegisterView(View):
    template_name = 'app_auth/register.html'
    forms_class = RegisterForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(to="quote:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, context={"form": self.forms_class})

    def post(self, request):
        form = self.forms_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            messages.success(request, message=f"Вітаємо {username}. Ваш акаунт успішно створено.")
            return redirect(to="app_auth:signin")
        return render(request, self.template_name, context={"form": form})

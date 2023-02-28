from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from .tokens import account_activation_token

User = get_user_model()


def activate_account(request, uidb64, token):
    print("activating account")
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.is_verified = True
        user.save()
        messages.success(request, "Your account has been activated successfully.")
        return redirect("users:login")
    else:
        messages.error(request, "The activation link is invalid or has expired.")
        return redirect("/")

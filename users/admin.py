from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib import admin
from .models import CustomUser, Reporter


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_verified",
        "role",
    )
    list_filter = ("is_active", "is_verified", "role")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class ReporterAdmin(admin.ModelAdmin):
    list_display = ("user", "verified")
    list_filter = ("verified",)
    search_fields = ("user__email", "user__first_name", "user__last_name")
    ordering = ("user__email",)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Reporter, ReporterAdmin)

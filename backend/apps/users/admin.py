"""DarsPro — users admin."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email", "full_name", "plan", "is_staff", "created_at"]
    list_filter = ["plan", "is_staff", "is_active", "auth_provider"]
    search_fields = ["email", "full_name", "phone"]
    readonly_fields = ["id", "created_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Profil", {"fields": ("full_name", "phone", "telegram_id", "auth_provider")}),
        ("Tarif", {"fields": ("plan", "plan_expires_at")}),
        ("Ruxsatlar", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Sanalar", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2"),
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "started_at", "expires_at"]
    list_filter = ["plan", "status"]
    search_fields = ["user__email", "payment_ref"]

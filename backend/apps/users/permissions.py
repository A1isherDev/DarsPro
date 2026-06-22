"""DarsPro — maxsus permission'lar."""
from rest_framework.permissions import BasePermission

from .models import Plan


# Tarif darajalari tartibi (kvota/limit taqqoslash uchun)
PLAN_RANK = {Plan.FREE: 0, Plan.START: 1, Plan.PRO: 2, Plan.MAX: 3}


class HasPlan(BasePermission):
    """Foydalanuvchi kerakli yoki undan yuqori tarifda ekanligini tekshiradi.

    Ishlatish: permission_classes = [HasPlan.require("pro")]
    `user.effective_plan` ishlatiladi — muddati o'tgan tarif free hisoblanadi.
    """

    message = "Bu imkoniyat uchun tarifingiz yetarli emas."
    required_plan = Plan.START

    @classmethod
    def require(cls, plan):
        return type(f"HasPlan_{plan}", (cls,), {"required_plan": plan})

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return PLAN_RANK.get(user.effective_plan, 0) >= PLAN_RANK.get(
            self.required_plan, 0
        )


class IsOwner(BasePermission):
    """Faqat obyekt egasi (created_by) o'zgartira/o'chira oladi."""

    message = "Bu kontent sizga tegishli emas."

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "created_by", None)
        return owner is not None and owner == request.user

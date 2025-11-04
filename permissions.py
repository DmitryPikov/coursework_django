from django.contrib import messages
from django.shortcuts import redirect


class OwnerQuerysetMixin:
    """Фильтрация queryset - пользователь видит только своё, менеджер - всё"""

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, "role") and self.request.user.role == "manager":
            return queryset
        return queryset.filter(owner=self.request.user)


class OwnerEditPermissionMixin:
    """Проверка прав на редактирование/удаление"""

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if hasattr(request.user, "role") and request.user.role == "manager":
            return super().dispatch(request, *args, **kwargs)
        if obj.owner != request.user:
            messages.error(request, "У вас нет прав для редактирования этого объекта")
            return redirect("mailing:mailings_list")
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin:
    """Только для менеджеров"""

    def dispatch(self, request, *args, **kwargs):
        if not (hasattr(request.user, "role") and request.user.role == "manager"):
            messages.error(request, "У вас нет прав для доступа к этой странице")
            return redirect("mailing:mailings_list")
        return super().dispatch(request, *args, **kwargs)

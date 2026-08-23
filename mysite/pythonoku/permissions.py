from rest_framework.permissions import BasePermission, SAFE_METHODS


def has_teacher_access(user):
    """Единая проверка роли для кастомного админа и стандартного Django admin."""
    return bool(
        user
        and user.is_authenticated
        and (user.is_admin or user.is_staff or user.is_superuser)
    )


class IsTeacherAdmin(BasePermission):
    message = 'Доступ разрешён только преподавателю.'

    def has_permission(self, request, view):
        return has_teacher_access(request.user)


class IsStudent(BasePermission):
    message = 'Эта функция доступна только ученику.'

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and not has_teacher_access(request.user))


class IsTeacherAdminOrReadOnly(BasePermission):
    message = 'Изменять материалы может только преподаватель.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.method in SAFE_METHODS or has_teacher_access(request.user)


class IsSelfOrTeacherAdmin(BasePermission):
    message = 'Нельзя изменять профиль другого пользователя.'

    def has_object_permission(self, request, view, obj):
        return obj == request.user or has_teacher_access(request.user)

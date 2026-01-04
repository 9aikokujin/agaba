from rest_framework import permissions
from rest_framework.permissions import BasePermission
from order.models import Order
from products.models import ProductReview


class IsAdminOrReadOnly(BasePermission):
    """
    Позволяет администраторам изменять данные,
    остальным только читать.
    """

    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff


class IsAuthorOrSuperuser(BasePermission):
    """
    Проверяет, является ли пользователь автором объекта или суперпользователем.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        return obj.username == request.user


class ReadOnly(BasePermission):
    """Позволяет только чтение данных."""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True  # Разрешаем чтение всем
        return False


class IsSellerOrAdminOrReadOnly(BasePermission):
    """
    Разрешение для проверки, является ли пользователь
    продавцом или администратором.
    Если нет, разрешается только чтение.
    """

    def has_permission(self, request, view):
        """
        Проверяет права доступа на уровне запроса.
        """
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return request.user and request.user.is_authenticated and (
            request.user.role == 'seller' or request.user.is_staff
        )



class IsAdminOrManager(BasePermission):
    """
    Позволяет администраторам изменять данные,
    остальным только читать.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role in ['admin', 'manager']
        )



class IsOrderManager(permissions.BasePermission):
    """Проверяет, является ли пользователь менеджером заказа"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'manager_assignment') and obj.manager_assignment:
            return obj.manager_assignment.manager == request.user
        return False


class CanLeaveReview(permissions.BasePermission):
    """
    Проверяет, может ли пользователь оставить отзыв.
    Пользователь может оставить отзыв, если:
    - У него есть заказ на стадии Stage_4 для указанного товара.
    - Он еще не оставил отзыв для этого товара.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            product_id = request.data.get('product')
            if not product_id:
                return False

            has_order = Order.objects.filter(
                user=request.user,
                stage='Stage_4',
                product_id=product_id
            ).exists()

            has_review = ProductReview.objects.filter(
                user=request.user,
                product_id=product_id
            ).exists()

            return has_order and not has_review

        return True

    def has_object_permission(self, request, view, obj):
        """..."""
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser or request.user.role in [
            'moderator'
        ]


# РАЗЛИЧНЫЕ ОПЕРАЦИИ.

class OrderUpdatePermission(permissions.BasePermission):
    """
    Комплексная проверка прав для обновления заказа.
    Владелец заказа и менеджер привязанный к нему
    может поменять первоначальны взнос.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.user == request.user:
            return request.method == 'PATCH'

        if request.user.is_staff:
            return True

        if IsOrderManager().has_object_permission(request, view, obj):
            return request.method == 'PATCH'

        return False


class CanCreateDelivery(permissions.BasePermission):
    """Проверяет может ли пользователь создать доставку."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        order_id = request.data.get('order')
        if not order_id:
            return False

        try:
            order = Order.objects.get(pk=order_id)
            return order.user == request.user and order.stage == 'Stage_3'
        except Order.DoesNotExist:
            return False


class DeliveryAccessPermission(permissions.BasePermission):
    """Комплексная проверка прав для доставки."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (
                obj.user == request.user or
                obj.order.manager_assignment.manager == request.user or
                request.user.is_staff or
                obj.cargo.user == request.user
            )

        return (
            request.user.is_staff or
            obj.order.manager_assignment.manager == request.user
        )




class IsSuperuserOrBuh(BasePermission):
    """
    Проверяет, является ли пользователь суперюзером или имеет роль 'buh'.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated

        return request.user.is_superuser or request.user.role == 'buh'

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_superuser or request.user.role == 'buh'
        return True

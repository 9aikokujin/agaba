from rest_framework.routers import DefaultRouter

from ..views import orders as orders_views

router = DefaultRouter()
router.register(
    r'orders',
    orders_views.OrderViewSet,
    basename='order'
)
router.register(
    r'order-details',
    orders_views.OrderDetailViewSet,
    basename='order-detail'
)
router.register(
    r'order-manager-assignments',
    orders_views.OrderManagerAssignmentViewSet,
    basename='order-manager-assignment'
)
router.register(
    r'delivery-orders',
    orders_views.DeliveryOrderViewSet,
    basename='delivery-order'
)
router.register(
    r'delivery-details',
    orders_views.DetailDeliveryViewSet,
    basename='delivery-card'
)

urlpatterns = []

from rest_framework.routers import DefaultRouter

from ..views import balance as balance_views

router = DefaultRouter()
router.register(
    r'balance', balance_views.BalanceViewSet,
    basename='balance'
)
router.register(
    r'replenishments', balance_views.ReplenishmentViewSet,
    basename='replenishment'
)
router.register(
    r'withdrawals', balance_views.WithdrawalViewSet,
    basename='withdrawal'
)
router.register(
    r'order-operations', balance_views.OrderOperationViewSet,
    basename='order-operation'
)
router.register(
    r'all-operations', balance_views.AllOperationViewSet,
    basename='all-operation'
)
router.register(
    r'account-pdfs', balance_views.AccountPDFViewSet,
    basename='account-pdf'
)

urlpatterns = []

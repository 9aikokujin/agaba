from rest_framework.routers import DefaultRouter

from ..views import products as products_views

router = DefaultRouter()
router.register(
    r'products', products_views.ProductViewSet,
    basename='product'
)
router.register(
    r'price-history', products_views.PriceHistoryViewSet,
    basename='price-history'
)
router.register(
    r'questions', products_views.QuestionViewSet,
    basename='question'
)
router.register(
    r'comparisons', products_views.ComparisonViewSet,
    basename='comparison'
)
router.register(
    r'product-reviews', products_views.ProductReviewViewSet,
    basename='product-review'
)
router.register(
    r'favorites', products_views.FavoriteViewSet,
    basename='favorite'
)

urlpatterns = []

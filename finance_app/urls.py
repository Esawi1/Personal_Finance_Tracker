from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import (
    AccountViewSet,
    CategoryViewSet,
    TransactionViewSet,
    BudgetViewSet,
    dashboard,
    cards_summary,
    me,  # ✅ added here
)

router = DefaultRouter()
router.register('accounts', AccountViewSet, basename='accounts')
router.register('categories', CategoryViewSet, basename='categories')
router.register('transactions', TransactionViewSet, basename='transactions')
router.register('budgets', BudgetViewSet, basename='budgets')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/summary/cards/', cards_summary, name='cards-summary'),
    path('api/me/', me, name='me'),  # ✅ Added here safely
    path('api/', include(router.urls)),
    path('', dashboard, name='dashboard'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

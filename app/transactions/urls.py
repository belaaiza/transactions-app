from django.urls import path, include
from rest_framework.routers import DefaultRouter

from transactions import views


router = DefaultRouter()
router.register('transactions', views.TransactionViewSet)

app_name = 'transaction'

urlpatterns = [
    path('', include(router.urls)),
]

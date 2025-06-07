# payments/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet
from . import views
from .views import AccountDetailsCreateUpdateView

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-order/', views.create_order, name='create_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('account-details/', AccountDetailsCreateUpdateView.as_view(), name='account-details'),

]

# payments/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet
from . import views
from .views import AccountDetailsCreateUpdateView, MentorEarningDetailView
from .views import (
    InitiatePaymentView,
    PaymentCallbackView,
    CheckPaymentStatusView,
    RefundPaymentView,
)

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-order/', views.create_order, name='create_order'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('account-details/', AccountDetailsCreateUpdateView.as_view(), name='account-details'),
    path('mentor-earning/', MentorEarningDetailView.as_view(), name='mentor-earning-detail'),
    
    path("payment/initiate/", InitiatePaymentView.as_view(), name="initiate_payment"),
    path("payment/callback/", PaymentCallbackView.as_view(), name="payment_callback"),
    path("payment/status/", CheckPaymentStatusView.as_view(), name="check_payment_status"),
    path("payment/refund/", RefundPaymentView.as_view(), name="refund_payment"),
]


from django.urls import path
from .views import DataView, FAQDataView

urlpatterns = [
    path('universities/', DataView.as_view(), name='data_view'),
    path('faq/', FAQDataView.as_view(), name='data_view'),
]




# payments/views.py

from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
import json

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_order(request):
    if request.method == "POST":
        amount = 50000  # Amount in paise (₹500)
        currency = "INR"
        receipt = "order_rcptid_11"
        
        data = {
            "amount": amount,
            "currency": currency,
            "receipt": receipt,
        }

        order = client.order.create(data=data)
        return JsonResponse(order)
    return HttpResponseBadRequest("Invalid request method")

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            client.utility.verify_payment_signature(data)
            return JsonResponse({'status': 'Payment verified successfully'})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'Payment verification failed'}, status=400)
    return HttpResponseBadRequest("Invalid request method")




# payment/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import AccountDetails
from .serializers import AccountDetailsSerializer

class AccountDetailsCreateUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            account = AccountDetails.objects.get(user=user)
        except AccountDetails.DoesNotExist:
            return Response({"detail": "Account details not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AccountDetailsSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request):
        user = request.user
        try:
            account = AccountDetails.objects.get(user=user)
            serializer = AccountDetailsSerializer(account, data=request.data)
            is_update = True
        except AccountDetails.DoesNotExist:
            serializer = AccountDetailsSerializer(data=request.data)
            is_update = False

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_200_OK if is_update else status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


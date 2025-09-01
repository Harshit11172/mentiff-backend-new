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


# payments/views.py

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .models import MentorEarning
from .serializers import MentorEarningSerializer

class MentorEarningDetailView(RetrieveAPIView):
    serializer_class = MentorEarningSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return MentorEarning.objects.get(user=self.request.user)






# # PHONE PAY INTEGRATION!!!


# # payments/views.py
# import uuid
# from django.http import JsonResponse
# from django.views import View
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# from .models import SessionPayment, TransactionLog, CustomUser
# from payments.phonepe_client import PhonePeClient

# from decimal import Decimal



# @method_decorator(csrf_exempt, name="dispatch")
# class InitiatePaymentView(View):
#     def post(self, request, *args, **kwargs):
#         try:
#             data = json.loads(request.body)

#             mentor_id = data.get("mentor_id")
#             mentee_id = data.get("mentee_id")
#             session_id = data.get("session_id") or str(uuid.uuid4())
#             total_amount = Decimal(str(data.get("total_amount")))
#             callback_url = data.get("callback_url")

#             if not (mentor_id and mentee_id and total_amount):
#                 return JsonResponse({"error": "mentor_id, mentee_id, total_amount are required"}, status=400)

#             mentor = CustomUser.objects.get(id=mentor_id)
#             mentee = CustomUser.objects.get(id=mentee_id)

#             session_payment = SessionPayment.objects.create(
#                 mentor=mentor,
#                 mentee=mentee,
#                 session_id=session_id,
#                 total_amount=total_amount
#             )

#             # ✅ Create TransactionLog first with unique txn ID
#             transaction_log = TransactionLog.objects.create(
#                 session_payment=session_payment,
#                 transaction_id=str(uuid.uuid4()),   # our internal ID
#                 amount=total_amount,
#                 status="INITIATED"
#             )

#             # ✅ Call PhonePe API
#             client = PhonePeClient()
#             response = client.initiate_payment(session_payment, transaction_log)
#             print('response in initiate is: ')
#             print(response)

#             # ✅ Update transaction log with PhonePe response
#             transaction_log.status = response.get("status", "PENDING")
#             transaction_log.raw_response = response
#             transaction_log.save()

#             return JsonResponse({
#                 "payment_url": response.get("paymentUrl"),
#                 "transaction_id": transaction_log.transaction_id,
#                 "status": transaction_log.status,
#                 "session_id": session_id
#             })

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)



# @method_decorator(csrf_exempt, name="dispatch")
# class PaymentCallbackView(View):
#     """Handle PhonePe callback (success/failure)."""

#     def post(self, request, *args, **kwargs):
#         data = request.POST.dict()
#         session_id = data.get("sessionId")
#         status = data.get("status")

#         try:
#             session_payment = SessionPayment.objects.get(session_id=session_id)
#         except SessionPayment.DoesNotExist:
#             return JsonResponse({"error": "Invalid session ID"}, status=400)

#         # Update payment status
#         session_payment.status = status.upper()
#         session_payment.save()

#         # Log callback
#         TransactionLog.objects.create(
#             payment=session_payment,
#             transaction_id=data.get("transactionId"),
#             status=status,
#             raw_response=data
#         )

#         return JsonResponse({"message": "Callback processed"})





# class CheckPaymentStatusView(View):
#     """Check status of a payment session."""

#     def get(self, request, *args, **kwargs):
#         session_id = request.GET.get("session_id")

#         try:
#             session_payment = SessionPayment.objects.get(session_id=session_id)
#         except SessionPayment.DoesNotExist:
#             return JsonResponse({"error": "Invalid session ID"}, status=400)

#         client = PhonePeClient()
#         status_response = client.check_status(session_payment.session_id)

#         # Update DB if needed
#         session_payment.status = status_response.get("status", session_payment.status)
#         session_payment.save()

#         # Log status check
#         TransactionLog.objects.create(
#             payment=session_payment,
#             status=status_response.get("status"),
#             raw_response=status_response
#         )

#         return JsonResponse(status_response)


# class RefundPaymentView(View):
#     """Trigger a refund for a payment."""

#     def post(self, request, *args, **kwargs):
#         session_id = request.POST.get("session_id")
#         refund_amount = int(request.POST.get("amount", 0)) * 100  # in paise

#         try:
#             session_payment = SessionPayment.objects.get(session_id=session_id)
#         except SessionPayment.DoesNotExist:
#             return JsonResponse({"error": "Invalid session ID"}, status=400)

#         client = PhonePeClient()
#         refund_response = client.refund(session_payment.session_id, refund_amount)

#         # Log refund
#         TransactionLog.objects.create(
#             payment=session_payment,
#             refund_id=refund_response.get("refundId"),
#             refund_status=refund_response.get("status"),
#             raw_response=refund_response
#         )

#         return JsonResponse(refund_response)











# # PHONE PAY INTEGRATION!!!


# payments/views.py
import json
import uuid
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import SessionPayment, TransactionLog
from django.contrib.auth import get_user_model
from .models import Mentor, Mentee


User = get_user_model()
from payments.phonepe_client import PhonePeClient
from decimal import Decimal


@method_decorator(csrf_exempt, name="dispatch")
class InitiatePaymentView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            print(data)

            mentor_id = data.get("mentor_id")
            mentee_id = data.get("mentee_id")
            session_id = data.get("session_id") or str(uuid.uuid4())
            currency = data.get("currency")
            date = data.get("date")
            time_slot = data.get("time_slot")
            total_amount = Decimal(str(data.get("total_amount")))
            callback_url = data.get("callback_url")


            if not (mentor_id and mentee_id and total_amount):
                return JsonResponse({"error": "mentor_id, mentee_id, total_amount are required"}, status=400)


            mentor = Mentor.objects.get(id=mentor_id)
            print(f"mentor is {mentor}")
            mentee = Mentee.objects.get(id=mentee_id)
            print(f"mentee is {mentee}")


            # mentor = User.objects.get(id=mentor_id)
            
            # mentee = User.objects.get(id=mentee_id)
            

            # Create session payment
            session_payment = SessionPayment.objects.create(
                mentor=mentor.user,        # Pass CustomUser instance
                mentee=mentee.user,
                session_id=session_id,
                currency=currency,
                total_amount=total_amount,
                status="INITIATED"  # Set initial status
            )

            # Create TransactionLog with unique merchant_order_id (this will be used by PhonePe)
            merchant_order_id = str(uuid.uuid4())
            transaction_log = TransactionLog.objects.create(
                session_payment=session_payment,
                transaction_id=merchant_order_id,
                currency=currency , # This should match what we send to PhonePe
                amount=total_amount,
                status="INITIATED"
            )

            # Call PhonePe API
            client = PhonePeClient()
            response = client.initiate_payment(session_payment, transaction_log)
            
            if response.get("success"):
                # PhonePe transaction ID is not available at initiation
                # It will be populated when we check status later
                transaction_log.status = "PENDING"
                transaction_log.raw_response = response
                transaction_log.save()

                # Update session payment status
                session_payment.status = "PENDING"
                session_payment.save()

                return JsonResponse({
                    "success": True,
                    "payment_url": response.get("redirect_url"),
                    "merchant_order_id": merchant_order_id,
                    "session_id": session_id
                })
            else:
                transaction_log.status = "FAILED"
                transaction_log.raw_response = response
                transaction_log.save()
                
                session_payment.status = "FAILED"
                session_payment.save()
                
                return JsonResponse({
                    "success": False,
                    "error": response.get("message", "Payment initiation failed")
                }, status=400)

        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid mentor or mentee ID"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class PaymentCallbackView(View):
    """Handle PhonePe callback/redirect after payment."""
    
    def post(self, request, *args, **kwargs):
        try:
            # PhonePe sends data as form-encoded, not JSON
            print("PHONEPE HAS HIT THE CALLBACK API FROM THEIR SERVER!")
            merchant_order_id = request.POST.get("merchantOrderId")
            transaction_id = request.POST.get("transactionId")
            print("Data send is: ")
            print(request)

            if not merchant_order_id:
                return JsonResponse({"error": "Missing merchant order ID"}, status=400)

            # Find transaction by our merchant_order_id
            try:
                transaction_log = TransactionLog.objects.get(transaction_id=merchant_order_id)
                session_payment = transaction_log.session_payment
            except TransactionLog.DoesNotExist:
                return JsonResponse({"error": "Invalid merchant order ID"}, status=400)

            # Check payment status from PhonePe
            client = PhonePeClient()
            status_response = client.check_status(merchant_order_id)

            if status_response.get("success"):
                payment_data = status_response.get("data", {})
                payment_status = payment_data.get("state")
                
                # Map PhonePe statuses to our statuses
                status_mapping = {
                    "COMPLETED": "SUCCESS",
                    "SUCCESS": "SUCCESS",
                    "FAILED": "FAILED",
                    "PENDING": "PENDING"
                }
                
                mapped_status = status_mapping.get(payment_status, payment_status)
                
                # Update transaction log
                transaction_log.status = mapped_status
                transaction_log.phonepe_transaction_id = payment_data.get("transactionId")
                transaction_log.payment_method = payment_data.get("paymentInstrument", {}).get("type")
                transaction_log.raw_response = status_response
                transaction_log.save()
                
                # Update session payment
                session_payment.status = mapped_status
                if payment_data.get("paymentInstrument"):
                    session_payment.payment_method = payment_data.get("paymentInstrument", {}).get("type")
                session_payment.save()
                
                return JsonResponse({
                    "success": True,
                    "status": mapped_status,
                    "message": "Payment status updated"
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "Failed to verify payment status"
                }, status=400)
                
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get(self, request, *args, **kwargs):
        """Handle GET redirect from PhonePe (success/failure page)"""
        merchant_order_id = request.GET.get("merchantOrderId")
        
        if merchant_order_id:
            # Check status and redirect user accordingly
            client = PhonePeClient()
            status_response = client.check_status(merchant_order_id)
            
            if status_response.get("success"):
                payment_data = status_response.get("data", {})
                payment_status = payment_data.get("state")
                
                # Map PhonePe statuses to our statuses
                status_mapping = {
                    "COMPLETED": "SUCCESS", 
                    "SUCCESS": "SUCCESS",
                    "FAILED": "FAILED",
                    "PENDING": "PENDING"
                }
                
                mapped_status = status_mapping.get(payment_status, payment_status)
                
                if payment_status == "COMPLETED":
                    # Redirect to success page
                    return JsonResponse({"message": "Payment successful", "status": mapped_status})
                else:
                    return JsonResponse({"message": "Payment failed", "status": mapped_status})
        
        return JsonResponse({"error": "Invalid callback"}, status=400)


class CheckPaymentStatusView(View):
    """Check status of a payment using merchant_order_id."""

    def get(self, request, *args, **kwargs):
        merchant_order_id = request.GET.get("merchant_order_id")
        
        if not merchant_order_id:
            return JsonResponse({"error": "merchant_order_id is required"}, status=400)

        try:
            transaction_log = TransactionLog.objects.get(transaction_id=merchant_order_id)
            session_payment = transaction_log.session_payment
        except TransactionLog.DoesNotExist:
            return JsonResponse({"error": "Invalid merchant order ID"}, status=400)

        client = PhonePeClient()
        status_response = client.check_status(merchant_order_id)

        if status_response.get("success"):
            payment_data = status_response.get("data", {})
            payment_status = payment_data.get("state")
            
            # Map PhonePe statuses to our statuses
            status_mapping = {
                "COMPLETED": "SUCCESS",
                "SUCCESS": "SUCCESS", 
                "FAILED": "FAILED",
                "PENDING": "PENDING"
            }
            
            mapped_status = status_mapping.get(payment_status, payment_status)
            
            # Update our records
            transaction_log.status = mapped_status
            transaction_log.phonepe_transaction_id = payment_data.get("transactionId")
            transaction_log.payment_method = payment_data.get("paymentInstrument", {}).get("type")
            transaction_log.raw_response = status_response
            transaction_log.save()
            
            session_payment.status = mapped_status
            if payment_data.get("paymentInstrument"):
                session_payment.payment_method = payment_data.get("paymentInstrument", {}).get("type")
            session_payment.save()

            return JsonResponse({
                "success": True,
                "status": mapped_status,
                "amount": str(session_payment.total_amount),
                "session_id": session_payment.session_id,
                "data": payment_data
            })
        else:
            return JsonResponse({
                "success": False,
                "error": status_response.get("message", "Failed to check status")
            }, status=400)


@method_decorator(csrf_exempt, name="dispatch")
class RefundPaymentView(View):
    """Trigger a refund for a completed payment."""

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            merchant_order_id = data.get("merchant_order_id")
            refund_amount = data.get("refund_amount")  # in rupees
            
            if not (merchant_order_id and refund_amount):
                return JsonResponse({"error": "merchant_order_id and refund_amount are required"}, status=400)

            try:
                transaction_log = TransactionLog.objects.get(transaction_id=merchant_order_id)
                session_payment = transaction_log.session_payment
            except TransactionLog.DoesNotExist:
                return JsonResponse({"error": "Invalid merchant order ID"}, status=400)

            # Verify payment is completed before refunding
            if session_payment.status not in ["SUCCESS", "COMPLETED"]:
                return JsonResponse({"error": "Can only refund successful payments"}, status=400)

            refund_amount_decimal = Decimal(str(refund_amount))
            if refund_amount_decimal > session_payment.total_amount:
                return JsonResponse({"error": "Refund amount cannot exceed paid amount"}, status=400)

            client = PhonePeClient()
            refund_response = client.refund(
                merchant_order_id, 
                transaction_log.phonepe_transaction_id,
                int(refund_amount_decimal * 100)  # convert to paise
            )

            # Create refund log entry
            TransactionLog.objects.create(
                session_payment=session_payment,
                transaction_id=f"refund_{str(uuid.uuid4())}",
                amount=refund_amount_decimal,
                status="REFUND_INITIATED",
                phonepe_transaction_id=refund_response.get("refundId"),
                raw_response=refund_response
            )

            return JsonResponse(refund_response)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
# # payments/phonepe_client.py

# from django.conf import settings
# from uuid import uuid4
# from phonepe.sdk.pg.env import Env
# from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
# from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
# from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo


# class PhonePeClient:
#     def __init__(self):
#         self.client_id = settings.PHONEPE_CLIENT_ID
#         self.client_secret = settings.PHONEPE_CLIENT_SECRET
#         self.client_version = settings.PHONEPE_CLIENT_VERSION
#         self.redirect_url = settings.PHONEPE_REDIRECT_URL
#         self.callback_url = settings.PHONEPE_CALLBACK_URL  # keep for future use/logs

#         # Initialize SDK client
#         self.client = StandardCheckoutClient.get_instance(
#             client_id=self.client_id,
#             client_secret=self.client_secret,
#             client_version=self.client_version,
#             env=Env.SANDBOX if settings.DEBUG else Env.PROD,
#             should_publish_events=False
#         )

#     def initiate_payment(self, session_payment, transaction_log):
#         """ Initiates a PhonePe payment using V2 SDK """

#         unique_order_id = str(uuid4())
#         amount = int(session_payment.total_amount * 100)  # in paise

#         # Meta info (optional, you can remove if not needed)
#         meta_info = MetaInfo(
#             udf1=str(session_payment.mentee.id),
#             udf2="mentee-payment",
#             udf3="v2-api"
#         )

#         # ✅ Do NOT pass callback_url here (not supported in v2 build_request)
#         standard_pay_request = StandardCheckoutPayRequest.build_request(
#             merchant_order_id=unique_order_id,
#             amount=amount,
#             redirect_url=self.redirect_url,
#             meta_info=meta_info
#         )

#         # Call PhonePe API via SDK
#         standard_pay_response = self.client.pay(standard_pay_request)

#         return {
#             "order_id": unique_order_id,
#             "redirect_url": standard_pay_response.redirect_url,
#             "raw_response": standard_pay_response.__dict__  # for debugging
#         }









# payments/phonepe_client.py

from django.conf import settings
from uuid import uuid4
from phonepe.sdk.pg.env import Env
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
import logging

logger = logging.getLogger(__name__)


class PhonePeClient:
    def __init__(self):
        self.client_id = settings.PHONEPE_CLIENT_ID
        self.client_secret = settings.PHONEPE_CLIENT_SECRET
        self.client_version = settings.PHONEPE_CLIENT_VERSION
        self.redirect_url = settings.PHONEPE_REDIRECT_URL
        self.callback_url = getattr(settings, 'PHONEPE_CALLBACK_URL', None)

                
        from phonepe.sdk.pg import env
        print(dir(env.Env))

        # Initialize SDK client
        try:
            self.client = StandardCheckoutClient.get_instance(
                client_id=self.client_id,
                client_secret=self.client_secret,
                client_version=self.client_version,
                env=Env.SANDBOX if settings.PHONEPE_TEST else Env.PRODUCTION,
                should_publish_events=False
            )
        except Exception as e:
            logger.error(f"Failed to initialize PhonePe client: {e}")
            raise

    def initiate_payment(self, session_payment, transaction_log):
        """Initiates a PhonePe payment using V2 SDK"""
        try:
            merchant_order_id = transaction_log.transaction_id
            amount = int(session_payment.total_amount * 100)  # Convert to paise

            # Meta info for additional data
            meta_info = MetaInfo(
                udf1=str(session_payment.mentee.id),
                udf2=str(session_payment.mentor.id),
                udf3=session_payment.session_id
            )

            # Build payment request
            standard_pay_request = StandardCheckoutPayRequest.build_request(
                merchant_order_id=merchant_order_id,
                amount=amount,
                redirect_url=self.redirect_url,
                
                meta_info=meta_info
            )
            print(f"phonepe client payload {standard_pay_request}")
            # Call PhonePe API
            standard_pay_response = self.client.pay(standard_pay_request)
            
            # Debug: Log the response attributes
            logger.info(f"PhonePe payment initiated: {merchant_order_id}")
            logger.debug(f"Response attributes: {dir(standard_pay_response)}")
            logger.debug(f"Response redirect_url: {standard_pay_response.redirect_url}")

            # StandardCheckoutPayResponse only contains redirect_url
            # PhonePe's transaction ID will be available later via status check
            return {
                "success": True,
                "redirect_url": standard_pay_response.redirect_url,
                "merchant_order_id": merchant_order_id,
                "raw_response": {
                    "redirect_url": standard_pay_response.redirect_url,
                    "response_type": "StandardCheckoutPayResponse",
                    "available_attributes": dir(standard_pay_response)
                }
            }

        except Exception as e:
            logger.error(f"PhonePe payment initiation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Payment initiation failed"
            }

    def check_status(self, merchant_order_id):
        """Check payment status using merchant_order_id"""
        try:
            status_response = self.client.check_status(merchant_order_id)
            
            logger.info(f"Status check for {merchant_order_id}: {status_response}")
            
            return {
                "success": True,
                "data": {
                    "transactionId": status_response.transaction_id,
                    "state": status_response.state,
                    "responseCode": status_response.response_code,
                    "amount": status_response.amount,
                    "merchantOrderId": merchant_order_id
                },
                "raw_response": status_response.__dict__
            }

        except Exception as e:
            logger.error(f"Status check failed for {merchant_order_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Status check failed"
            }

    def refund(self, merchant_order_id, phonepe_transaction_id, refund_amount_paise):
        """Initiate refund for a transaction"""
        try:
            # Generate unique refund ID
            refund_id = f"refund_{str(uuid4())}"
            
            # Note: You'll need to check the actual SDK method for refunds
            # This is a placeholder - adjust based on actual SDK
            refund_response = self.client.refund(
                merchant_order_id=merchant_order_id,
                transaction_id=phonepe_transaction_id,
                refund_id=refund_id,
                amount=refund_amount_paise
            )
            
            logger.info(f"Refund initiated: {refund_id} for {merchant_order_id}")
            
            return {
                "success": True,
                "refundId": refund_id,
                "status": "REFUND_INITIATED",
                "amount": refund_amount_paise,
                "raw_response": refund_response.__dict__ if hasattr(refund_response, '__dict__') else str(refund_response)
            }

        except Exception as e:
            logger.error(f"Refund failed for {merchant_order_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Refund initiation failed"
            }
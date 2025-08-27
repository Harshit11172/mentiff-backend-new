# payments/phonepe_client.py

import hashlib, json, base64, requests
from django.conf import settings


class PhonePeClient:
    BASE_URL = settings.PHONEPE_BASE_URL 
    print(f"base url is {BASE_URL}")
    # "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1"
    # PHONEPE_BASE_URL=https://api-preprod.phonepe.com/apis/pg-sandbox


    def __init__(self):
        self.merchant_id = settings.PHONEPE_MERCHANT_ID
        self.api_key = settings.PHONEPE_API_KEY
        self.key_index = settings.PHONEPE_KEY_INDEX
        self.redirect_url = settings.PHONEPE_REDIRECT_URL
        self.callback_url = settings.PHONEPE_CALLBACK_URL

    def _generate_checksum(self, payload: dict) -> tuple[str, str]:
        """
        PhonePe checksum format:
        base64encodedPayload + "/pg/v1/pay" + apiKey
        """
        encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        string_to_hash = encoded_payload + "/pg/v1/pay" + self.api_key
        checksum = hashlib.sha256(string_to_hash.encode()).hexdigest() + "###" + str(self.key_index)
        return encoded_payload, checksum
    

    def initiate_payment(self, session_payment, transaction_log):
        payload = {
            "merchantId": self.merchant_id,
            "merchantTransactionId": transaction_log.transaction_id,
            "merchantUserId": str(session_payment.mentee.id),
            "amount": int(session_payment.total_amount * 100),  # in paise
            "redirectUrl": self.redirect_url,
            "redirectMode": "POST",
            "callbackUrl": self.callback_url,
            "paymentInstrument": {"type": "PAY_PAGE"}
        }

        encoded_payload, checksum = self._generate_checksum(payload)
        print(checksum)
        print(self.merchant_id)
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum,
            "X-MERCHANT-ID": self.merchant_id,
        }

        url = f"{self.BASE_URL}/pay"
        print(url)
        response = requests.post(url, json={"request": encoded_payload}, headers=headers)
        print('response from phonepe is')
        print(response.json())
        return response.json()

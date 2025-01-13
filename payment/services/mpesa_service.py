import base64
import requests
import datetime
import json
from django.conf import settings

class MpesaService:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.base_url = settings.MPESA_BASE_URL
        self.passkey = settings.MPESA_PASSKEY
        self.business_shortcode = settings.MPESA_BUSINESS_SHORTCODE

    def get_access_token(self):
        """
        Generate Mpesa API access token
        """
        auth_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        auth_headers = {
            'Authorization': f'Basic {base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()}'
        }
        
        response = requests.get(auth_url, headers=auth_headers)
        return response.json().get('access_token')

    def initiate_stk_push(self, phone_number, amount, order_id):
        """
        Initiate Mpesa STK Push
        """
        access_token = self.get_access_token()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        password = base64.b64encode(f"{self.business_shortcode}{self.passkey}{timestamp}".encode()).decode()
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{settings.SITE_URL}/payments/mpesa/callback/",
            "AccountReference": str(order_id),
            "TransactionDesc": f"Payment for Order #{order_id}"
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest", 
            json=payload, 
            headers=headers
        )
        
        return response.json()
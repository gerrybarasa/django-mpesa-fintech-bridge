import request
import base64
from datetime import datetime
from django.conf import settings
from request.auth import HTTPBasicAuth

def get_access_token():
    """Generates the OAuth token required for all Daraja API calls."""
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = request.get(url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
        return response.json().get("access_token")
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

def initiate_stk_push(phone_number, amount, account_ref):
    """Triggers the STK Push prompt on the user's phone."""
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Password = Base64(ShortCode + PassKey + Timestamp)
    password_str = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode('utf-8')
    
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": "Payment for services"
    }
    
    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    response = request.post(url, json=payload, headers=headers)
    return response.json()
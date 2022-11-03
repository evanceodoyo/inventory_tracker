import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from decouple import config



class MpesaC2BCredential:
    consumer_key = config('CONSUMER_KEY')
    consumer_secret = config('CONSUMER_SECRET')
    api_URL = config('API_URL')


class MpesaAccessToken:
    r = requests.get(
        MpesaC2BCredential.api_URL,
        auth=HTTPBasicAuth(
            MpesaC2BCredential.consumer_key, MpesaC2BCredential.consumer_secret
        ),
    )
    mpesa_acces_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_acces_token["access_token"]


class LipaNaMpesaPassword:
    lipa_time = datetime.now().strftime("%Y%m%d%H%M%S")
    business_short_code = config('BUSINESS_SHORT_CODE')
    passkey = config('PASSKEY')
    data_to_encode = business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode("utf-8")

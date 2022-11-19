from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import requests
import json
# from requests.auth import HTTPBasicAuth

from payments.models import MpesaPayment
from . mpesa_credentials import MpesaAccessToken, LipaNaMpesaPassword
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def lipa_na_mpesa_online(request, phone, amount):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {"Authorization": f"Bearer {access_token}"}
    request = {
        "BusinessShortCode": LipaNaMpesaPassword.business_short_code,    
        "Password": LipaNaMpesaPassword.decode_password,    
        "Timestamp": LipaNaMpesaPassword.lipa_time,    
        "TransactionType": "CustomerPayBillOnline",    
        "Amount": amount,    
        "PartyA": phone,    
        "PartyB": LipaNaMpesaPassword.business_short_code,    
        "PhoneNumber": phone,    
        "CallBackURL":"https://mydomain.com/pat",    
        "AccountReference":"Mosioma Retailers",    
        "TransactionDesc":"Testing STK Push"
    }
    response = requests.post(api_url, json=request, headers=headers)
    return HttpResponse('success')


@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'
    headers = {"Authorization": f'"Bearer {access_token}"'}
    options = {
        "ShortCode": LipaNaMpesaPassword.business_short_code,
        "ResponseType": "Completed",
        "ConfirmationURL": "https://9f61-196-216-92-57.in.ngrok.io/payment/c2b/confirmation",
        "ValidationURL": "https://9f61-196-216-92-57.in.ngrok.io/payment/c2b/validation",
    }
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)

@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body = request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)

    payment = MpesaPayment(
        order = '',
        first_name = mpesa_payment['FirstName'],
        last_name = mpesa_payment['LastName'],
        middle_name = mpesa_payment['MiddleName'],
        description = mpesa_payment['TransID'],
        phone_number = mpesa_payment['MSISDN'],
        amount = mpesa_payment['TransAmount'],
        reference = mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type = mpesa_payment['TransactionType',]
    )
    payment.save()

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
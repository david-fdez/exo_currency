from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from exo_currency_app.serializers import UserSerializer, GroupSerializer, CurrencyRatesSerializer

import requests
from django.http import JsonResponse


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class CurrencyRatesViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = CurrencyRatesSerializer

def currencyRatesHistory(request):
    # TODO this should be done following a "driver" pattern
    # TODO verify all parameters are there and format
    # TODO verify dateFrom is in the past
    dateFromString = request.GET.get('dateFrom')
    dateToString = request.GET.get('dateTo')



    #TODO import in header instead
    from datetime import datetime, timedelta, date
    dateFrom = datetime.strptime(dateFromString, '%Y-%m-%d').date()
    # if no dateTo is specified: dateTo = currentDate
    dateTo = date.today() if dateToString is None else datetime.strptime(dateToString, '%Y-%m-%d').date()

    # TODO not hardcode currencies
    allCurrencies = "EUR,CHF,USD,GBP"

    dateToCurrencyRates = dict()
    while dateFrom <= dateTo :
        # TODO factorise this code
        accessKey = "71536a9dda6d9e466c6b74066f341948"
        url = "http://data.fixer.io/api/{0}?access_key={1}&symbols={2}".format(dateFrom, accessKey, allCurrencies)
        response = requests.get(url)
        if response.status_code == 200:
            responseContent = response.json()
            dateToCurrencyRates[dateFrom.strftime("%Y-%m-%d")] = responseContent.get('rates')
        else: 
            pass # TODO return with an error
        dateFrom = dateFrom + timedelta(1)
        
    return JsonResponse({'dateFrom': dateFrom, 'dateTo': dateTo, 'dateToCurrencyRates': dateToCurrencyRates})


def currencyExchange(request):
    # TODO this should be done following a "driver" pattern
    # TODO verify all parameters are there and format
    # TODO access key should not be hardcoded
    accessKey = "71536a9dda6d9e466c6b74066f341948"
    originCurrency = request.GET.get('originCurrency')
    targetCurrency = request.GET.get('targetCurrency')
    amount = request.GET.get('amount')

    # url = "http://data.fixer.io/api/convert?access_key={0}&from={1}&to={2}&amount={3}".format(accessKey, originCurrency, targetCurrency, amount)
    url = "http://data.fixer.io/api/latest?access_key={}".format(accessKey)
    response = requests.get(url)
    if response.status_code == 200:
        responseContent = response.json()
        originCurrencyEuroExchangeRate = float(responseContent.get('rates').get(originCurrency))
        targetCurrencyEuroExchangeRate = float(responseContent.get('rates').get(targetCurrency))
        result = float(amount) * targetCurrencyEuroExchangeRate / originCurrencyEuroExchangeRate
        return JsonResponse({'result': round(result,2), 'originCurrency': originCurrency, 'targetCurrency': targetCurrency, 'amount': amount })
    # TODO actually send error status blabla
    return JsonResponse({'test':'not worked'})

def timeWeightedRateOfReturn(request):
    # TODO this should be done following a "driver" pattern
    # TODO verify all parameters are there and format
    # TODO access key should not be hardcoded
    accessKey = "71536a9dda6d9e466c6b74066f341948"
    originCurrency = request.GET.get('originCurrency')
    targetCurrency = request.GET.get('targetCurrency')
    initialAmount = float(request.GET.get('amount'))
    dateInvested = request.GET.get('dateInvested')

    investmentDateRatesUrl = "http://data.fixer.io/api/{0}?access_key={1}&symbols={2},{3}".format(dateInvested, accessKey, originCurrency, targetCurrency)    
    investmentDateRatesResponse = requests.get(investmentDateRatesUrl)

    currentRatesUrl = "http://data.fixer.io/api/latest?access_key={}".format(accessKey)
    currentRatesResponse = requests.get(currentRatesUrl)

    if investmentDateRatesResponse.status_code == 200 and currentRatesResponse.status_code == 200 :
        investmentDatesResponseContent = investmentDateRatesResponse.json()
        currentRatesResponseContent = currentRatesResponse.json()
        # TODO factorise this code
        originCurrencyInitialExchangeRate = float(investmentDatesResponseContent.get('rates').get(originCurrency))
        targetCurrencyInitialExchangeRate = float(investmentDatesResponseContent.get('rates').get(targetCurrency))
        amountInTargetCurrency = initialAmount * targetCurrencyInitialExchangeRate / originCurrencyInitialExchangeRate

        # TODO factorise this code
        currentOriginCurrencyExchangeRate = float(currentRatesResponseContent.get('rates').get(originCurrency))
        currentTargetCurrencyExchangeRate = float(currentRatesResponseContent.get('rates').get(targetCurrency))
        currentValueInSourceCurrency = amountInTargetCurrency * currentOriginCurrencyExchangeRate / currentTargetCurrencyExchangeRate

        # if no cash flow since investment: TimeWeightedRateOfReturn = RateOfReturn
        percentageRateOfReturn = (currentValueInSourceCurrency - initialAmount) * 100 / initialAmount
        return JsonResponse({'result': round(percentageRateOfReturn,2), 'originCurrency': originCurrency, 'targetCurrency': targetCurrency, 'amount': request.GET.get('amount'), 'dateInvested': dateInvested })
    # TODO actually send error status blabla
    return JsonResponse({'test':'not worked'})



from django.shortcuts import render
from datetime import datetime, timedelta, date


from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from exo_currency_app.models import FixerCurrencyRates, MockCurrencyRates, FixerCurrencyExchange, MockCurrencyExchange

import requests
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError


def getCurrencyRatesHistory(request):
    dateFromString = request.GET.get('dateFrom')
    dateToString = request.GET.get('dateTo')

    try:
        # if no dateTo or dateFrom value provided, default value is today
        dateFrom = date.today() if dateFromString is None else datetime.strptime(dateFromString, '%Y-%m-%d').date()
        dateTo = date.today() if dateToString is None else datetime.strptime(dateToString, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseBadRequest("dateFrom and/or dateTo parameters wrong format")

    if dateFrom > date.today() or dateTo > date.today():
        return HttpResponseBadRequest("dateFrom and dateTo cannot be in the future")

    try:
        # TODO should use "driver" pattern (polymorphism)
        currencyRatesModel = FixerCurrencyRates # MockCurrencyRates
        result = currencyRatesModel(dateFrom, dateTo).listCurrencyRates()
    except:
        return HttpResponseServerError("Internal error")
    return JsonResponse(result)


def getCurrencyExchange(request):
    originCurrency = request.GET.get('originCurrency')
    targetCurrency = request.GET.get('targetCurrency')
    amount = request.GET.get('amount')

    if originCurrency is None or targetCurrency is None or amount is None:
        return HttpResponseBadRequest("originCurrency, targetCurrency and amount are required parameters")

    try:
        amount = float(amount)
    except ValueError:
        return HttpResponseBadRequest("amount must be a float")

    try:
        # TODO should use "driver" pattern (polymorphism)
        currencyExchangeModel =  FixerCurrencyExchange # MockCurrencyExchange
        result = currencyExchangeModel(originCurrency, targetCurrency, amount).calculate()        
    except:
        return HttpResponseServerError("Internal error")
    return JsonResponse(result)

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



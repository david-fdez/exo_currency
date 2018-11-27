from django.shortcuts import render
from datetime import datetime, timedelta, date


from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from exo_currency_app.models import FixerCurrencyRates, MockCurrencyRates, FixerCurrencyExchange, MockCurrencyExchange, FixerTimeWeightedRateOfReturn

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
        return HttpResponseBadRequest("dateFrom and/or dateTo parameters wrong format: must be YYYY-MM-DD")

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

def getTimeWeightedRateOfReturn(request):
    originCurrency = request.GET.get('originCurrency')
    targetCurrency = request.GET.get('targetCurrency')
    initialAmount = request.GET.get('amount')
    dateInvested = request.GET.get('dateInvested')

    if originCurrency is None or targetCurrency is None or initialAmount is None or dateInvested is None:
        return HttpResponseBadRequest("originCurrency, targetCurrency, amount and dateInvested are required parameters")
    
    try:
        dateInvested = datetime.strptime(dateInvested, '%Y-%m-%d').date()
        if dateInvested > date.today():
            return HttpResponseBadRequest("dateInvested cannot be in the future")
    except ValueError:
        return HttpResponseBadRequest("dateInvested wrong format: must be YYYY-MM-DD")

    try:
        initialAmount = float(initialAmount)
    except ValueError:
        return HttpResponseBadRequest("amount must be a float")

    try:
    # TODO should use "driver" pattern (polymorphism)
        timeWeightedRateOfReturnModel =  FixerTimeWeightedRateOfReturn
        result = timeWeightedRateOfReturnModel(originCurrency, targetCurrency, initialAmount, dateInvested).calculate()        
    except:
        return HttpResponseServerError("Internal error")
    return JsonResponse(result)
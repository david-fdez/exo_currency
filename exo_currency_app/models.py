from django.db import models
import requests, random
from datetime import datetime, timedelta, date

from django.conf import settings

accessKey = settings.FIXERIO_ACCESS_KEY
allCurrencies = ["EUR", "CHF", "USD", "GBP"]

class CurrencyRatesFactory():
    def create(self, dateFrom, dateTo):
        if settings.CURRENCY_PROVIDER == "MOCK":
            return MockCurrencyRates(dateFrom, dateTo)
        else:
            return FixerCurrencyRates(dateFrom, dateTo)

class FixerCurrencyRates():
    def __init__(self, dateFrom, dateTo):
        self.dateFrom = dateFrom
        self.dateTo = dateTo
        self.dateToCurrencyRates = dict()

    def listCurrencyRates(self):
        dateFromCopy = self.dateFrom
        while dateFromCopy <= self.dateTo :
            url = "http://data.fixer.io/api/{0}?access_key={1}&symbols={2}".format(dateFromCopy, accessKey, ",".join(allCurrencies))
            response = requests.get(url)
            if response.status_code == 200:
                responseContent = response.json()
                self.dateToCurrencyRates[dateFromCopy.strftime("%Y-%m-%d")] = responseContent.get('rates')
            else: 
                print(response)
                raise "Error retrieving data from fixer.io"
            dateFromCopy = dateFromCopy + timedelta(1)
            
        return { 'dateFrom': self.dateFrom, 'dateTo': self.dateTo, 'dateToCurrencyRates': self.dateToCurrencyRates }

class MockCurrencyRates():
    def __init__(self, dateFrom, dateTo):
        self.dateFrom = dateFrom
        self.dateTo = dateTo
        self.dateToCurrencyRates = dict()

    def listCurrencyRates(self):
        dateFromCopy = self.dateFrom
        while dateFromCopy <= self.dateTo :
            dateFromCopyString = dateFromCopy.strftime("%Y-%m-%d")
            self.dateToCurrencyRates[dateFromCopyString] = dict()

            for currency in allCurrencies:
                self.dateToCurrencyRates[dateFromCopyString][currency] = round(random.uniform(0, 150), 2)

            dateFromCopy = dateFromCopy + timedelta(1)
            
        return { 'dateFrom': self.dateFrom, 'dateTo': self.dateTo, 'dateToCurrencyRates': self.dateToCurrencyRates }



class CurrencyExchangeFactory():
    def create(self, originCurrency, targetCurrency, amount):
        if settings.CURRENCY_PROVIDER == "MOCK":
            return MockCurrencyExchange(originCurrency, targetCurrency, amount) 
        else:
            return FixerCurrencyExchange(originCurrency, targetCurrency, amount)

class FixerCurrencyExchange():
    def __init__(self, originCurrency, targetCurrency, amount):
        self.originCurrency = originCurrency
        self.targetCurrency = targetCurrency
        self.amount = amount

    def calculate(self):
        url = "http://data.fixer.io/api/latest?access_key={}".format(accessKey)
        response = requests.get(url)
        if response.status_code == 200:
            responseContent = response.json()
            originCurrencyEuroExchangeRate = float(responseContent.get('rates').get(self.originCurrency))
            targetCurrencyEuroExchangeRate = float(responseContent.get('rates').get(self.targetCurrency))
            result = self.amount * targetCurrencyEuroExchangeRate / originCurrencyEuroExchangeRate
            return {'result': round(result,2), 'originCurrency': self.originCurrency, 'targetCurrency': self.targetCurrency, 'amount': self.amount }    
        else:
            print(response)
            raise "Error retrieving data from fixer.io"    

class MockCurrencyExchange():
    def __init__(self, originCurrency, targetCurrency, amount):
        self.originCurrency = originCurrency
        self.targetCurrency = targetCurrency
        self.amount = amount

    def calculate(self):
        result = round(random.uniform(0, 150), 2)
        return {'result': round(result,2), 'originCurrency': self.originCurrency, 'targetCurrency': self.targetCurrency, 'amount': self.amount }    


class TimeWeightedRateOfReturnFactory():
    def create(self, originCurrency, targetCurrency, amount, dateInvested):
        if settings.CURRENCY_PROVIDER == "MOCK":
            return MockTimeWeightedRateOfReturn(originCurrency, targetCurrency, amount, dateInvested) 
        else:
            return FixerTimeWeightedRateOfReturn(originCurrency, targetCurrency, amount, dateInvested)


class FixerTimeWeightedRateOfReturn():
    def __init__(self, originCurrency, targetCurrency, amount, dateInvested):
        self.originCurrency = originCurrency
        self.targetCurrency = targetCurrency
        self.amount = amount
        self.dateInvested = dateInvested

    def calculate(self):
        investedDateCurrencyRates = FixerCurrencyRates(self.dateInvested, self.dateInvested).listCurrencyRates()
        originCurrencyInitialExchangeRate = float(investedDateCurrencyRates.get('dateToCurrencyRates').get(str(self.dateInvested)).get(self.originCurrency))
        targetCurrencyInitialExchangeRate = float(investedDateCurrencyRates.get('dateToCurrencyRates').get(str(self.dateInvested)).get(self.targetCurrency))
        amountInTargetCurrency = self.amount * targetCurrencyInitialExchangeRate / originCurrencyInitialExchangeRate

        currentValueInSourceCurrency = FixerCurrencyExchange(originCurrency = self.targetCurrency, targetCurrency = self.originCurrency, amount = amountInTargetCurrency).calculate()['result']

        # if no cash flow since investment: TimeWeightedRateOfReturn = RateOfReturn
        percentageRateOfReturn = (currentValueInSourceCurrency - self.amount) * 100 / self.amount
        return {'result': round(percentageRateOfReturn,2), 'originCurrency': self.originCurrency, 'targetCurrency': self.targetCurrency, 'amount': self.amount, 'dateInvested': self.dateInvested }


class MockTimeWeightedRateOfReturn():
    def __init__(self, originCurrency, targetCurrency, amount, dateInvested):
        self.originCurrency = originCurrency
        self.targetCurrency = targetCurrency
        self.amount = amount
        self.dateInvested = dateInvested

    def calculate(self):
        result = round(random.uniform(0, 150), 2) * self.amount
        return {'result': result, 'originCurrency': self.originCurrency, 'targetCurrency': self.targetCurrency, 'amount': self.amount, 'dateInvested': self.dateInvested }


    
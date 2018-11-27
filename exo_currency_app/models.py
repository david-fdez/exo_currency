from django.db import models
import requests, random
from datetime import datetime, timedelta, date

# TODO these date (accessKey, currencies) should not be hardcoded here
accessKey = "71536a9dda6d9e466c6b74066f341948"
allCurrencies = ["EUR", "CHF", "USD", "GBP"]

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
            raise "Error retrieving data from fixer.io"    

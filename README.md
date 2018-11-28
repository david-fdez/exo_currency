# exo_currency

The backoffice chart requires installing pygal: `pip install pygal`

The exchange rates API consists mainly of three endpoints:
* /currencyRatesHistory with parameters dateFrom (default value: today) and dateTo (default value: today)
* /currencyCalculations/exchange with parameters originCurrency (required), targetCurrency (required) and amount (required)
* /currencyCalculations/twrr with parameters originCurrency (required), targetCurrency (required), amount (required) and dateInvested (required)

The backoffice chart can be viewed on:
* /backoffice/exchangeRateEvolution

Two implementations of the exchange rate can be used: one relying on the provider Fixer.io and another one using mock values. To use one or another, set the variable CURRENCY_PROVIDER in settings.py to "FIXER.IO" or to "MOCK". Default implementation relies on Fixer.io

Unfortunately, I haven't had the time yet to implement some features of the application, such as unit testing or the optional features mentioned in the exercice description: "batch procedure to reitreve exchange rates" and "API versioning / scope".

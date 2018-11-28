import pygal

mockCurrencyExchangeData = {
        'USD' :     [1.65, 1.60, 1.52, 1.53, 1.70, 1.80, 1.60, 1.45, 1.20, 1.15, 1.25],
        'CHF' :     [1.13,    1, 0.95, 1.10, 1.15, 1.20, 1.30, 1.20, 1.20, 1.17, 1.10],
        'GBP' :     [0.89, 0.85, 0.80, 0.75, 0.82, 0.89, 0.90, 0.95, 0.92, 0.90, 0.89]
}


class BackOfficeCurrencyExchangeChart():
    def __init__(self, **kwargs):
        self.chart = pygal.Line(**kwargs)
        self.chart.title = 'Exchange rates evolution (to EUR)'
        self.chart.x_labels = [str(month) + '/18' for month in range(1, 12)]

    def generate(self):
        # Add data to lines
        for key, value in mockCurrencyExchangeData.items():
            self.chart.add(key, value)

        # Return the SVG rendered
        return self.chart.render(is_unicode=True)
import pygal

from exo_currency_app.models import Fruit


class FruitPieChart():

    def __init__(self, **kwargs):
        self.chart = pygal.Pie(**kwargs)
        self.chart.title = 'Amount of Fruits'

    def get_data(self):
        '''
        Query the db for chart data, pack them into a dict and return it.
        '''
        # data = {}
        # for fruit in Fruit.objects.all():
        #     data[fruit.name] = fruit.amt
        # return data
        data = dict()
        data['apples'] = 9
        data['oranges'] = 21
        data['pears'] = 15
        data['grapes'] = 12
        data['strawberries'] = 6
        return data


    def generate(self):
        # Get chart data
        chart_data = self.get_data()

        # Add data to chart
        for key, value in chart_data.items():
            self.chart.add(key, value)

        # Return the rendered SVG
        return self.chart.render(is_unicode=True)
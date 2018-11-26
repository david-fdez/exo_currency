from django.contrib.auth.models import User, Group
from exo_currency_app.models import CurrencyRates 
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class CurrencyRatesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CurrencyRates
        fields = ('created', 'title')  

# class CurrencyRatesSerializer(serializers.Serializer):
    # class Meta:
    #     model = CurrencyRates
    #     fields = ('created', 'title')        
from rest_framework import serializers
from .models import Account, Consumer


class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = ['id', 'name', 'address', 'ssn']


class AccountSerializer(serializers.ModelSerializer):
    consumers = ConsumerSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'client_reference', 'balance', 'status', 'consumers']

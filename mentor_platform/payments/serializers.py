# payments/serializers.py

from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'  # Or specify fields explicitly if needed

    def create(self, validated_data):
        return Transaction.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.mentee = validated_data.get('mentee', instance.mentee)
        instance.mentor = validated_data.get('mentor', instance.mentor)
        instance.session_fee = validated_data.get('session_fee', instance.session_fee)
        instance.transaction_date = validated_data.get('transaction_date', instance.transaction_date)
        instance.payment_status = validated_data.get('payment_status', instance.payment_status)
        instance.session_date = validated_data.get('session_date', instance.session_date)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        return instance


from rest_framework import serializers
from .models import AccountDetails

class UserInfoSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    user_type = serializers.CharField()

class AccountDetailsSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = AccountDetails
        fields = ['account_holder_name', 'bank_name', 'bank_account_number', 'ifsc_code', 'upi_id', 'user']




# payments/serializers.py

from rest_framework import serializers
from .models import MentorEarning

class MentorEarningSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MentorEarning
        fields = ['id', 'username', 'balance', 'total_earnings', 'amount_requested', 'updated_at']

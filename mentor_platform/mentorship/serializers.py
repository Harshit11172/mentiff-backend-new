# mentorship/serializers.py

from rest_framework import serializers
from .models import Session

from rest_framework import serializers
from users.models import MentorAvailability


class MentorAvailabilitySerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = MentorAvailability
        fields = ['id', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time']




class SessionSerializer(serializers.ModelSerializer):
    payment_reference = serializers.CharField(write_only=True)
    end_time = serializers.SerializerMethodField()  # ✅ Tell DRF it's a computed field

    class Meta:
        model = Session
        fields = [
            'mentor', 'amount_paid',
            'date', 'start_time', 'duration_minutes',
            'end_time', 'payment_reference'
        ]

    def validate_payment_reference(self, value):
        # Replace this with real logic
        if not self._fake_verify_payment(value):
            raise serializers.ValidationError("Invalid or unverified payment reference.")
        return value

    def _fake_verify_payment(self, payment_id):
        # TODO: integrate real payment gateway verification here
        return payment_id.startswith("PAY_")  # dummy check

    def create(self, validated_data):
        validated_data.pop('payment_reference', None)
        mentee = self.context['request'].user

        # ❌ Avoid mentee duplication
        validated_data.pop('mentee', None)

        return Session.objects.create(mentee=mentee, **validated_data)
    
    def get_end_time(self, obj):
        return obj.get_end_time()

from rest_framework import serializers
from .models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Feedback
        fields = ['id', 'type', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

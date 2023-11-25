from rest_framework import serializers
from .models import User
from movies.serializers import TicketSerializer

class UserSerializer(serializers.ModelSerializer):
    ticket_set = TicketSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        social = validated_data.pop('social', False)  
        first_name = validated_data.pop('first_name', '')  
        last_name = validated_data.pop('last_name', '') 

        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password'],
            gender = validated_data['gender'],
            birth = validated_data['birth'],
            social = social,
            first_name = first_name,
            last_name = last_name
        )
        return user
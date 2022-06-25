from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from versatileimagefield.serializers import VersatileImageFieldSerializer

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator
 
from apps.agents.models import Agent
 
class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"detail": "Password fields didn't match."})
        elif len(attrs['password']) < 5:
            raise serializers.ValidationError({"detail": "Password length cannot be less than 5 characters."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        user = self.context['request'].user

        if user.pk != instance.pk or not user.is_active:
            raise serializers.ValidationError({"detail": "You dont have permission for this action."})

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class UpdateUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(read_only=True)
    avatar = VersatileImageFieldSerializer(
        sizes='product_headshot',
        required=False,
    )
    is_email_verified = serializers.CharField(read_only=True)
    is_cell_verified = serializers.CharField(read_only=True)
    is_active_agent = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'cell', 'first_name', 'last_name', 'email', 'avatar', 'is_email_verified', 'is_cell_verified', 'is_active_agent')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def update(self, instance, validated_data):
        user = self.context['request'].user
        
        try:
            if user.pk != instance.pk or not user.is_active:
                raise serializers.ValidationError("You dont have permission for this action.")

            if get_user_model().objects.exclude(pk=user.pk).filter(cell=validated_data['cell']).exists():
                raise serializers.ValidationError("This cell is already in use.")

            if 'avatar' in validated_data:
                instance.avatar = validated_data['avatar']

            instance.first_name = validated_data['first_name']
            instance.last_name = validated_data['last_name']
            instance.cell = validated_data['cell']

            if 'email' in validated_data:
                validated_data.pop('email', None)

            instance.save()

        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})

        return instance

    def get_is_active_agent(self, obj):
        try:
            agent = Agent.objects.get(agent__user=self.context['request'].user)
            return agent.active
        except Exception as e:
            return False


class DeleteUserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('cell', 'first_name', 'last_name', 'email')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    def create(self, validated_data):
        return

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk or not user.is_active:
            raise serializers.ValidationError({"detail": "You dont have permission for this action."})

        instance.is_active = False

        instance.save()
        return instance
    
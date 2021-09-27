from django.contrib.auth import get_user_model
from django.dispatch import Signal
from django.conf import settings

from rest_framework import serializers

from control.models import Control

from .models import UserProfile

from keycloak import KeycloakAdmin


User = get_user_model()

# These signals are triggered after the user is created/updated via the API
user_api_post_add = Signal(providing_args=['user_profile', 'control'])
user_api_post_update = Signal(providing_args=['user_profile'])


class RemoveControlSerializer(serializers.Serializer):
    control = serializers.PrimaryKeyRelatedField(queryset=Control.objects.all())


class UserProfileSerializer(serializers.ModelSerializer, KeycloakAdmin):
    id = serializers.IntegerField(source='user.pk', read_only=True)
    control = serializers.PrimaryKeyRelatedField(
        queryset=Control.objects.all(), write_only=True, required=False)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = UserProfile
        fields = (
            'id', 'first_name', 'last_name', 'email', 'profile_type',
            'organization', 'control', 'is_audited', 'is_inspector')

    def create(self, validated_data):
        print(settings.KEYCLOAK_URL)
        print(settings.KEYCLOAK_REALM)
        print(settings.OIDC_RP_CLIENT_SECRET)
        print(settings.KEYCLOAK_ADMIN_USERNAME)
        print(settings.KEYCLOAK_ADMIN_PASSWORD)
        keycloak_admin = KeycloakAdmin(server_url=settings.KEYCLOAK_URL,
                               username=settings.KEYCLOAK_ADMIN_USERNAME,
                               password=settings.KEYCLOAK_ADMIN_PASSWORD,
                               realm_name=settings.KEYCLOAK_REALM,
                               client_id=settings.OIDC_RP_CLIENT_ID,
                               verify=False)
        print("On est juste après")
        profile_data = validated_data
        control = profile_data.pop('control', None)
        user_data = profile_data.pop('user')

        # lowercase the email
        email = user_data.get('email')
        if email:
            email = email.lower()
        user_data['username'] = email

        # Find if user already exists.
        profile = UserProfile.objects.filter(user__username=email).first()

        session_user = self.context['request'].user
        if control and control not in session_user.profile.controls.active():
            raise serializers.ValidationError(
                f"{session_user} n'est pas authorisé à modifier ce contrôle: {control}")
        should_receive_email_report = False
        if profile_data.get('profile_type') == UserProfile.INSPECTOR:
            should_receive_email_report = True
        if profile:
            print("On est dedans")
            profile.user.first_name = user_data.get('first_name')
            profile.user.last_name = user_data.get('last_name')
            profile.organization = profile_data.get('organization')
            profile.profile_type = profile_data.get('profile_type')
            profile.send_files_report = should_receive_email_report
            profile.user.save()
            profile.save()
            keycloak_admin.create_user({"email": email,
                    "username": email,
                    "enabled": True,
                    "firstName": profile.user.first_name,
                    "lastName": profile.user.last_name}) 
        else:
            user = User.objects.create(**user_data)
            profile_data['user'] = user
            profile_data['send_files_report'] = should_receive_email_report
            profile = UserProfile.objects.create(**profile_data)
        if control:
            profile.controls.add(control)
        if control:
            user_api_post_add.send(
                sender=UserProfile, session_user=session_user, user_profile=profile,
                control=control)
        else:
            user_api_post_update.send(
                sender=UserProfile, session_user=session_user, user_profile=profile)
        return profile

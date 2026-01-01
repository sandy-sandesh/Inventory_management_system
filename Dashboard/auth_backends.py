from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """Authenticate with either username or email (case-insensitive)."""
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        identifier = username or kwargs.get('email')
        if identifier is None or password is None:
            return None
        try:
            user = UserModel.objects.get(Q(username__iexact=identifier) | Q(email__iexact=identifier))
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

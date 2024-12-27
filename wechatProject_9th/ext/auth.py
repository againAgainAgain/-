from rest_framework.authentication import BaseAuthentication

from app01 import models


class RecordAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        token = request.query_params.get('token')
        if not token:
            return None,token

        instance = models.User.objects.filter(token=token).first()
        if not instance:
            return instance

        return instance,token
        # raise NotImplementedError(".authenticate() must be overridden.")

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return "API"
# SPDX-License-Identifier: AGPL-3.0-or-later
from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.providers.base.views import BaseLoginView
from django.utils.decorators import method_decorator
from django.views import View

from . import protocol
from .provider import DiscourseConnectProvider


@method_decorator(login_not_required, name="dispatch")
class LoginView(BaseLoginView):
    provider_id = DiscourseConnectProvider.id


@method_decorator(login_not_required, name="dispatch")
class CallbackView(View):
    def get(self, request):
        provider = get_adapter().get_provider(request, DiscourseConnectProvider.id)
        try:
            data, state_id = protocol.verify_response(
                provider.app.secret,
                request.GET.get("sso", ""),
                request.GET.get("sig", ""),
                request.session,
            )
        except protocol.InvalidPayloadError as e:
            return render_authentication_error(request, provider=provider, exception=e)
        login = provider.sociallogin_from_response(request, data)
        login.state = provider.unstash_redirect_state(request, state_id)
        return complete_social_login(request, login)


login = LoginView.as_view()
callback = CallbackView.as_view()

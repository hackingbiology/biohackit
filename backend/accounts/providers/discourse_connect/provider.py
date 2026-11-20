# SPDX-License-Identifier: AGPL-3.0-or-later
"""Generic DiscourseConnect (SSO) provider for django-allauth.

Instance used by biohack.it: ``rapamycin_news``. Configured through
SOCIALACCOUNT_PROVIDERS["discourse_connect"]["APPS"]: client_id = instance
slug, secret = shared SSO secret, settings["url"] = forum base URL.
"""

from allauth.socialaccount.providers.base import Provider, ProviderAccount
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode

from . import protocol


class DiscourseConnectAccount(ProviderAccount):
    def get_profile_url(self):
        base = self.account.extra_data.get("_base_url", "").rstrip("/")
        username = self.account.extra_data.get("username")
        return f"{base}/u/{username}" if base and username else None

    def to_str(self):
        return self.account.extra_data.get("username") or super().to_str()


def _verified(data) -> bool:
    # Discourse sends require_activation=true while it has not confirmed
    # the address itself.
    return data.get("require_activation", "false") != "true"


class DiscourseConnectProvider(Provider):
    id = "discourse_connect"
    name = "Discourse"
    account_class = DiscourseConnectAccount
    supports_redirect = True

    @property
    def base_url(self) -> str:
        return (self.app.settings.get("url") or "").rstrip("/")

    def get_login_url(self, request: HttpRequest, **kwargs):
        url = reverse("discourse_connect_login")
        if kwargs:
            url = f"{url}?{urlencode(kwargs)}"
        return url

    def redirect(self, request, process, next_url=None, data=None, **kwargs):
        state = self.stash_redirect_state(request, process, next_url, data, **kwargs)
        return_url = request.build_absolute_uri(reverse("discourse_connect_callback"))
        nonce = protocol.issue_nonce(request.session, state)
        payload, sig = protocol.build_request(
            self.app.secret, nonce=nonce, return_sso_url=return_url
        )
        url = f"{self.base_url}/session/sso_provider?" + urlencode(
            {"sso": payload, "sig": sig}
        )
        return HttpResponseRedirect(url)

    def extract_uid(self, data):
        return str(data["external_id"])

    def extract_extra_data(self, data):
        extra = {
            k: data[k]
            for k in ("external_id", "username", "name", "email")
            if k in data
        }
        extra["_base_url"] = self.base_url
        return extra

    def extract_common_fields(self, data):
        return {
            "email": data.get("email"),
            "username": data.get("username"),
            "name": data.get("name"),
            "email_verified": _verified(data),
        }

    def extract_email_addresses(self, data):
        from allauth.account.models import EmailAddress

        if not data.get("email"):
            return []
        return [
            EmailAddress(email=data["email"], verified=_verified(data), primary=True)
        ]


provider_classes = [DiscourseConnectProvider]

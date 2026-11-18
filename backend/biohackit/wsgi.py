# SPDX-License-Identifier: AGPL-3.0-or-later
# biohack.it — open-source biohacking platform
# Copyright (C) HackingBiology 2026 — https://biohack.it
# Full license text: https://www.gnu.org/licenses/agpl-3.0.html

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biohackit.settings")

application = get_wsgi_application()

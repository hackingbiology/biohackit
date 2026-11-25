# SPDX-License-Identifier: AGPL-3.0-or-later
from django.contrib import admin

from .models import OptimalRange, ReferenceRange, SafetyThreshold

admin.site.register([ReferenceRange, OptimalRange, SafetyThreshold])

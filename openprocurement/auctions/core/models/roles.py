# -*- coding: utf-8 -*-
from schematics.transforms import (
    blacklist,
    whitelist
)
from openprocurement.api.models.auction_models import (
    schematics_default_role,
)
from openprocurement.api.models.common import (
    sensitive_embedded_role,
)


view_complaint_role = (blacklist('owner_token', 'owner') + schematics_default_role)
auction_embedded_role = sensitive_embedded_role

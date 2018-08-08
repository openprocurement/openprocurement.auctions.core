# -*- coding: utf-8 -*-
from zope.deprecation import moved


message = "openprocurement.auctions.core.models now contains submodules: schema, validators and roles. "
"Please, re-import your stuff from there"

moved('openprocurement.auctions.core.models.schema', message)
moved('openprocurement.auctions.core.models.roles', message)
moved('openprocurement.auctions.core.models.validators', message)

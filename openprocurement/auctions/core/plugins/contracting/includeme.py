# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.contracting.v1 import includeme as v1
from openprocurement.auctions.core.plugins.contracting.v2 import includeme as v2
from openprocurement.auctions.core.plugins.contracting.v2_1 import includeme as v2_1
from openprocurement.auctions.core.plugins.contracting.v3 import includeme as v3
from openprocurement.auctions.core.plugins.contracting.v3_1 import includeme as v3_1


def includeme(config):
    v1.includeme(config)
    v2.includeme(config)
    v2_1.includeme(config)
    v3.includeme(config)
    v3_1.includeme(config)

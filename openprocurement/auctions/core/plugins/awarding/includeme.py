# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.v1 import includeme as v1
from openprocurement.auctions.core.plugins.awarding.v2 import includeme as v2
from openprocurement.auctions.core.plugins.awarding.v3 import includeme as v3


def includeme(config):
    v1.includeme(config)
    v2.includeme(config)
    v3.includeme(config)

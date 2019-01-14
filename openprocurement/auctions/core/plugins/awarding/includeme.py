# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.v1 import includeme as v1
from openprocurement.auctions.core.plugins.awarding.v2 import includeme as v2
from openprocurement.auctions.core.plugins.awarding.v2_1 import includeme as v2_1
from openprocurement.auctions.core.plugins.awarding.v3 import includeme as v3
from openprocurement.auctions.core.plugins.awarding.v3_1 import includeme as v3_1
from openprocurement.auctions.core.plugins.awarding.v3_2 import includeme as v3_2


def includeme(config):
    config.scan("openprocurement.auctions.core.plugins.awarding.base.views")
    v1.includeme(config)
    v2.includeme(config)
    v2_1.includeme(config)
    v3.includeme(config)
    v3_1.includeme(config)
    v3_2.includeme(config)

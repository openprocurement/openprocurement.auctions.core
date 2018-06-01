# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.base.interfaces import (
    IAwardManagerAdapter,
)


def includeme(config):
    from .adapters import AwardManagerV3_1Adapter
    from .interfaces import IAwardV3_1
    config.registry.registerAdapter(
        AwardManagerV3_1Adapter,
        (IAwardV3_1, ),
        IAwardManagerAdapter
    )
    config.scan("openprocurement.auctions.core.plugins.awarding.v3_1.views")

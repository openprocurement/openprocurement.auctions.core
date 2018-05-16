# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.base.interfaces import (
    IAwardManagerAdapter,
)


def includeme(config):
    from .adapters import AwardManagerV2Adapter
    from .interfaces import IAwardV2
    config.registry.registerAdapter(
        AwardManagerV2Adapter,
        (IAwardV2, ),
        IAwardManagerAdapter
    )
    config.scan("openprocurement.auctions.core.plugins.awarding.v2.views")

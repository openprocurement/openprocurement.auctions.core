# -*- coding: utf-8 -*-
from openprocurement.auctions.core.plugins.awarding.base.interfaces import (
    IAwardManagerAdapter,
)


def includeme(config):
    from .adapters import AwardManagerV3_2Adapter
    from .interfaces import IAwardV3_2
    config.registry.registerAdapter(
        AwardManagerV3_2Adapter,
        (IAwardV3_2, ),
        IAwardManagerAdapter
    )
